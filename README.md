# Ireland IT Job Monitor (Agentic Emailer)

This script watches common ATS providers (Greenhouse & Lever) for **roles located in Ireland**, builds a compact summary (company, role, description, required experience, skills, company website, and apply link), and **emails you only the new ones**.

## Quickstart

1. **Download** these files.
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Edit `config.yaml`:
   - Put your SMTP credentials (Gmail, Outlook, or any SMTP).
   - Switch `email.enabled` to `true` when ready.
   - Add/remove companies by slug.
4. Run a one-off scan:
   ```bash
   python job_monitor.py --once
   ```
   If email is disabled, it writes an `latest_email_preview.html` for you to open.
5. To run periodically on your machine:
   ```bash
   while true; do python job_monitor.py --once; sleep 3600; done
   ```

### GitHub Actions (optional, free scheduler)

- Create a new **private** repo, commit these files, and push.
- In the repo, go to **Settings → Secrets and variables → Actions** and add:
  - `SMTP_HOST` (e.g., `smtp.gmail.com`)
  - `SMTP_PORT` (`587` for TLS)
  - `SMTP_USER`
  - `SMTP_PASSWORD`
  - `MAIL_FROM`
  - `MAIL_TO`
- Adjust the cron in `.github/workflows/job_monitor.yml` (default: every 2 hours).

## How it works

- **Greenhouse**: `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true`
- **Lever**: `https://api.lever.co/v0/postings/{slug}?mode=json`
- Filters locations by Irish counties/cities and "Remote - Ireland".
- Naively extracts **experience** and **skills** from descriptions.
- Keeps a `state.json` of jobs already emailed so you only get **new** ones.

> Many Irish & EU companies use Workday/Ashby/Teamtailor/etc. You can extend the script by adding fetchers. For Workday, endpoints differ per tenant; for Ashby and Workable many boards expose JSON. PRs welcome!

## Notes

- Respect each site's Terms of Service. This uses public JSON endpoints exposed by the ATS.
- Add as many companies as you like; the script is light-weight.
- If you prefer a daily digest rather than every discovery, schedule via the GitHub Action. 
