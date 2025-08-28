import requests, yaml, re
from bs4 import BeautifulSoup
from pathlib import Path

CONFIG_PATH = Path('config.yaml')

# ----------------- Utilities -----------------
def slugify(name):
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s

# ----------------- Fetch companies -----------------
def fetch_wikipedia_it_companies():
    url = 'https://en.wikipedia.org/wiki/List_of_companies_of_Ireland'
    resp = requests.get(url, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    companies = set()

    # Grab all wikitable tables
    tables = soup.select('table.wikitable')
    for table in tables:
        for row in table.select('tr'):
            cell = row.select_one('td a')
            if cell:
                name = cell.get_text(strip=True)
                if name:
                    companies.add(name)
    return sorted(companies)

# ----------------- Update config -----------------
def update_config_with_companies(companies):
    cfg = yaml.safe_load(CONFIG_PATH.read_text())
    if cfg is None:
        cfg = {}
    if 'greenhouse_companies' not in cfg: cfg['greenhouse_companies'] = []
    if 'lever_companies' not in cfg: cfg['lever_companies'] = []

    added_count = 0
    for c in companies:
        slug = slugify(c)
        if not any(d.get('slug') == slug for d in cfg['greenhouse_companies']):
            cfg['greenhouse_companies'].append({'slug': slug, 'website': ''})
            added_count += 1
        if not any(d.get('slug') == slug for d in cfg['lever_companies']):
            cfg['lever_companies'].append({'slug': slug})
            added_count += 1

    CONFIG_PATH.write_text(yaml.dump(cfg))
    print(f'Added {added_count} companies to config.yaml')

# ----------------- Main -----------------
if __name__ == '__main__':
    companies = fetch_wikipedia_it_companies()
    update_config_with_companies(companies)
