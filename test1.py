# import requests
# from bs4 import BeautifulSoup
# import csv
# from urllib.parse import urljoin

# base_url = "https://www.ibec.ie"
# directory_url = "https://www.ibec.ie/technologyireland/about-us/member-directory"

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
# }

# response = requests.get(directory_url, headers=headers)
# soup = BeautifulSoup(response.text, 'html.parser')

# companies = []

# for link in soup.select("div.logos-grid a[href]"):
#     relative_href = link.get('href')
#     website = urljoin(base_url, relative_href)  # converts relative URL to full URL
#     img_tag = link.find('img')
#     if img_tag and img_tag.get('alt'):
#         name = img_tag['alt'].strip()
#         companies.append({"name": name, "website": website})

# # Save to CSV
# with open("technology_ireland_companies.csv", "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=["name", "website"])
#     writer.writeheader()
#     for company in companies:
#         writer.writerow(company)

# print(f"Saved {len(companies)} companies to technology_ireland_companies.csv")

#---------------------------------------------------------------------------------------------------------------------------#

# import requests
# from bs4 import BeautifulSoup
# import csv
# import time
# from urllib.parse import urljoin, urlparse, urlunparse

# BASE_URL = "https://techbehemoths.com"

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
# }

# all_companies = []

# def clean_url(url):
#     parsed = urlparse(url)
#     return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

# page = 1
# while True:
#     url = f"{BASE_URL}/companies/ireland?page={page}"
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")

#     company_cards = soup.select("article.co-box")
#     if not company_cards:
#         break

#     for card in company_cards:
#         name_tag = card.select_one("p.co-box__name a")
#         profile_path = name_tag.get('href') if name_tag else None
#         name = name_tag.text.strip() if name_tag else None
#         if name:
#             name = " ".join(name.split())  # clean extra newlines/spaces

#         if profile_path:
#             profile_url = urljoin(BASE_URL, profile_path)

#             # Visit company profile page to get website
#             profile_resp = requests.get(profile_url, headers=headers)
#             profile_soup = BeautifulSoup(profile_resp.text, "html.parser")

#             website_tag = profile_soup.select_one("a[href^='http']")
#             website = website_tag['href'].strip() if website_tag else None
#             if website:
#                 website = clean_url(website)  # remove UTM and extra params

#             all_companies.append({"name": name, "website": website})
#             print(f"Scraped: {name} -> {website}")
#             time.sleep(1)  # polite delay

#     page += 1
#     time.sleep(1)

# # Save to CSV
# with open("techbehemoths_companies_clean.csv", "w", newline="", encoding="utf-8") as f:
#     writer = csv.DictWriter(f, fieldnames=["name", "website"])
#     writer.writeheader()
#     for company in all_companies:
#         writer.writerow(company)

# print(f"Saved {len(all_companies)} companies to techbehemoths_companies_clean.csv")

#---------------------------------------------------------------------------------------------------------------------------#

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv

BASE_URL = "https://www.goodfirms.co/directory/country/top-software-development-companies/ireland"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/google-chrome" 

service = Service('/home/suhas/chromedriver-linux64/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://www.goodfirms.co/directory/country/top-software-development-companies/ireland"
driver.get(url)
time.sleep(5)  # wait for JS

print(driver.title)  # should print page title
print(len(driver.page_source))  # length of page HTML

with open("debug.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

driver.quit()


