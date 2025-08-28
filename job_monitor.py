import requests, re, time, yaml, logging, json, smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('job-monitor')

CONFIG_PATH = Path('config.yaml')
STATE_PATH = Path('state.json')

# ----------------- Utilities -----------------
def slugify(name):
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s

def validate_greenhouse_slug(slug):
    url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return True
    except requests.exceptions.HTTPError:
        logger.warning('Invalid Greenhouse slug: %s', slug)
        return False

def validate_lever_slug(slug):
    url = f'https://api.lever.co/v0/postings/{slug}?mode=json'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return True
    except requests.exceptions.HTTPError:
        logger.warning('Invalid Lever slug: %s', slug)
        return False

def fetch_irishjobs(search_url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            r = requests.get(search_url, timeout=60)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            items = []
            for job_el in soup.select('div.job-result'):
                title_el = job_el.select_one('h2.job-title a')
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                url = title_el['href']
                if not url.startswith('http'):
                    url = 'https://www.irishjobs.ie' + url
                company = job_el.select_one('div.job-result__company')
                location = job_el.select_one('li.job-result__location')
                summary = job_el.select_one('div.job-result__snippet')
                company_name = company.get_text(strip=True) if company else 'Unknown'
                loc = location.get_text(strip=True) if location else ''
                summ = summary.get_text(strip=True) if summary else ''
                items.append({'source':'irishjobs','company':company_name,'title':title,'location':loc,'url':url,'summary':summ,'posted_at':datetime.utcnow().isoformat()})
            return items
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            logger.warning('[IrishJobs] Attempt %d failed: %s', attempt+1, e)
            time.sleep(delay)
    logger.warning('[IrishJobs] Failed to fetch %s after %d attempts', search_url, retries)
    return []

# ----------------- Job Fetchers -----------------
def fetch_greenhouse_jobs(slug):
    if not validate_greenhouse_slug(slug):
        return []
    url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true'
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    jobs = []
    for j in resp.json().get('jobs', []):
        jobs.append({'source':'greenhouse','company':slug,'title':j['title'],'url':j['absolute_url'],'location':j.get('location', ''),'summary':j.get('content', ''),'posted_at':j.get('updated_at', datetime.utcnow().isoformat())})
    return jobs

def fetch_lever_jobs(slug):
    if not validate_lever_slug(slug):
        return []
    url = f'https://api.lever.co/v0/postings/{slug}?mode=json'
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    jobs = []
    for j in resp.json():
        jobs.append({'source':'lever','company':slug,'title':j['text'],'url':j['applyUrl'],'location':j.get('categories', {}).get('location', ''),'summary':j.get('description', ''),'posted_at':j.get('date', datetime.utcnow().isoformat())})
    return jobs

# ----------------- Email -----------------
def send_email(jobs, cfg):
    body = ''
    for j in jobs:
        body += f"{j['company']} | {j['title']} | {j['location']}\n{j['url']}\n\n"
    if not body:
        logger.info('No new jobs to send.')
        return

    msg = MIMEText(body)
    msg['Subject'] = cfg['email']['subject']
    msg['From'] = cfg['email']['from']
    msg['To'] = ','.join(cfg['email']['to'])

    s = smtplib.SMTP(cfg['email']['host'], cfg['email']['port'])
    s.starttls()
    s.login(cfg['email']['user'], cfg['email']['password'])
    s.send_message(msg)
    s.quit()
    logger.info('Email sent with %d jobs', len(jobs))

# ----------------- Main -----------------
if __name__ == '__main__':
    import argparse
    import fetch_ireland_it_companies

    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--update-companies', action='store_true')
    args = parser.parse_args()

    if args.update_companies:
        companies = fetch_ireland_it_companies.fetch_wikipedia_it_companies()
        fetch_ireland_it_companies.update_config_with_companies(companies)
        print('Updated config.yaml with IT companies from Wikipedia')
        exit(0)

    cfg = yaml.safe_load(CONFIG_PATH.read_text())
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}

    all_jobs = []

    # Greenhouse
    for c in cfg.get('greenhouse_companies', []):
        try:
            jobs = fetch_greenhouse_jobs(c['slug'])
            all_jobs.extend(jobs)
        except Exception as e:
            logger.warning('Greenhouse %s error: %s', c['slug'], e)

    # Lever
    for c in cfg.get('lever_companies', []):
        try:
            jobs = fetch_lever_jobs(c['slug'])
            all_jobs.extend(jobs)
        except Exception as e:
            logger.warning('Lever %s error: %s', c['slug'], e)

    # Filter unseen jobs
    new_jobs = [j for j in all_jobs if j['url'] not in state]
    for j in new_jobs:
        state[j['url']] = datetime.utcnow().isoformat()

    STATE_PATH.write_text(json.dumps(state, indent=2))

    # Send email or preview
    if cfg['email'].get('enabled'):
        send_email(new_jobs, cfg)
    else:
        Path('latest_email_preview.html').write_text('\n'.join([f"{j['company']} | {j['title']} | {j['location']} | {j['url']}" for j in new_jobs]))
        logger.info('Preview written to latest_email_preview.html')
