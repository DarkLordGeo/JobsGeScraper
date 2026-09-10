"""Interactive CLI scraper for jobs.ge.

Prompts for a category, then scrapes every listing in it into jobs.json.
Output schema (jobs.json is a plain JSON array, one entry per job):

    {
        "job_id": "672911",
        "company": "...",
        "position": "...",
        "date": ["<start>", "<expiry>"],
        "desciption": ["<full description text>"],
        "job_link": "https://www.jobs.ge/ge/?view=jobs&id=672911"
    }

This mirrors the scraping logic in DarkLordGeo/ITJobsBackend's devjobs.py,
which scrapes the IT/Programming category on an automated daily schedule.
The two are kept in sync by hand since they live in separate repos with
different entry points (this one is interactive; that one runs unattended).
"""

import json
import time
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.jobs.ge"
REQUEST_TIMEOUT = 15
PAGE_DELAY_SECONDS = 5
DETAIL_DELAY_SECONDS = 1.5
FULL_PAGE_ROW_COUNT = 300
APPLY_LINK_TEXT = "აქ"
ENGLISH_LINK_TEXT = "ინგლისურ ენაზე"
JOBS_FILE = "jobs.json"

# (category label, jobs.ge category id) - order matches the site's own menu.
CATEGORIES = [
    ("ადმინისტრაცია/მენეჯმენტი", 1),
    ("ფინანსები/სტატისტიკა", 3),
    ("გაყიდვები", 2),
    ("PR/მარკეტინგი", 4),
    ("ზოგადი ტექნიკური პერსონალი", 18),
    ("ლოგისტიკა/ტრანსპორტი/დისტრიბუცია", 5),
    ("მშენებლობა/რემონტი", 11),
    ("დასუფთავება", 16),
    ("დაცვა/უსაფრთხოება", 17),
    ("IT/პროგრამირება", 6),
    ("მედია/გამომცემლობა", 13),
    ("განათლება", 12),
    ("სამართალი", 7),
    ("მედიცინა/ფარმაცია", 8),
    ("სილამაზე/მოდა", 14),
    ("კვება", 10),
    ("სხვა", 9),
]


def print_logo():
    print(
        r"""
      __   __   __      __   __   __
   | /  \ |__) /__`    /__` /  ` |__)  /\  |__) |__  |__)
\__/ \__/ |__) .__/    .__/ \__, |  \ /~~\ |    |___ |  \

github: https://github.com/DarkLordGeo
        """
    )


def prompt_category():
    for index, (label, _cid) in enumerate(CATEGORIES):
        print(index, label)

    choice = int(input("Choose which category you want to scrape: "))
    label, cid = CATEGORIES[choice]
    template_url = (
        f"https://www.jobs.ge/?page={{page}}&q=&cid={cid}&lid=0&jid=0"
        "&in_title=0&has_salary=0&is_ge=0&for_scroll=yes"
    )
    return label, template_url


def get_soup(url):
    """GET a URL and parse it, returning None (and logging) on any failure."""
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to fetch {url}: {exc}")
        return None
    return BeautifulSoup(response.text, "html.parser")


def fetch_listing_rows(template_url):
    """Fetch every listing page until a short page signals the last one."""
    rows = []
    page = 0
    while True:
        page += 1
        soup = get_soup(template_url.format(page=page))
        if soup is None:
            break

        page_rows = soup.find_all("tr")
        rows.extend(page_rows)
        print(f"Accessed page {page} ({len(page_rows)} rows)")

        if len(page_rows) < FULL_PAGE_ROW_COUNT:
            print(f"End of job listing found on page {page}, saving...")
            break
        time.sleep(PAGE_DELAY_SECONDS)

    return rows


def extract_job_id(href):
    """Pull the numeric jobs.ge job id out of a listing anchor's href."""
    query = parse_qs(urlparse(href).query)
    return query.get("id", [None])[0]


def fetch_description(detail_url):
    """Return a job's description text.

    Follows the "view in English" link when a posting only exposes one, and
    returns None for postings that only link out to an external application
    form (nothing to scrape) or when the page can't be fetched/parsed.
    """
    soup = get_soup(detail_url)
    if soup is None:
        return None

    dtable = soup.find("table", {"class": "dtable"})
    if dtable is None:
        return None

    anchors = dtable.find_all("a")

    if len(anchors) == 2 and anchors[-1].get_text(strip=True) == APPLY_LINK_TEXT:
        return None

    if len(anchors) == 2 and anchors[-1].get_text(strip=True) == ENGLISH_LINK_TEXT:
        english_url = urljoin(BASE_URL, anchors[-1].get("href", ""))
        soup = get_soup(english_url)
        dtable = soup.find("table", {"class": "dtable"}) if soup else None

    if dtable is None:
        return None

    rows = dtable.find_all("tr")
    return rows[-1].get_text() if rows else None


def parse_row(row):
    """Turn one listing <tr> into a job record, or None if it isn't one."""
    tds = row.find_all("td")
    if len(tds) < 6:
        return None

    anchor = row.find("a")
    href = anchor.get("href") if anchor else None
    if not href:
        return None

    job_id = extract_job_id(href)
    if job_id is None:
        return None

    fields = [td.get_text(strip=True) for td in tds if td.get_text(strip=True)]
    if len(fields) < 4:
        return None

    company, position, start_date, expire_date = fields[:4]

    return {
        "job_id": job_id,
        "company": company,
        "position": position,
        "date": [start_date, expire_date],
        "job_link": urljoin(BASE_URL, href),
    }


def write_jobs(jobs_by_id, path=JOBS_FILE):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(list(jobs_by_id.values()), file, ensure_ascii=False, indent=2)


def scrape_category(template_url, delay_between_jobs=DETAIL_DELAY_SECONDS):
    """Scrape every listing behind template_url, writing jobs.json after each
    job so a crash partway through a run still leaves usable progress."""
    jobs_by_id = {}

    for row in fetch_listing_rows(template_url):
        record = parse_row(row)
        if record is None:
            continue

        description = fetch_description(record["job_link"])
        record["desciption"] = [description] if description else []

        jobs_by_id[record["job_id"]] = record
        write_jobs(jobs_by_id)
        print(f"jobs scraped: {len(jobs_by_id)}")

        if delay_between_jobs:
            time.sleep(delay_between_jobs)

    return jobs_by_id


def main():
    print_logo()
    label, template_url = prompt_category()
    print(f"Scraping category: {label}")
    jobs = scrape_category(template_url)
    print(f"Done. Saved {len(jobs)} jobs to {JOBS_FILE}")


if __name__ == "__main__":
    main()
