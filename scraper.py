"""jobs.ge scraper.

Run interactively (`python scraper.py`) to pick one category from a prompt
and dump results to jobs.json, exactly as before. Can also be run
non-interactively (`python scraper.py --category 9`) or imported as a
module — `bot.py` and `notifier.py` use `scrape_category()` directly to
power the Telegram subscription feature.
"""
import argparse
import json
import time

import requests
from bs4 import BeautifulSoup

CATEGORIES = [
    {"name": "ადმინისტრაცია/მენეჯმენტი", "cid": 1},
    {"name": "ფინანსები/სტატისტიკა", "cid": 3},
    {"name": "გაყიდვები", "cid": 2},
    {"name": "PR/მარკეტინგი", "cid": 4},
    {"name": "ზოგადი ტექნიკური პერსონალი", "cid": 18},
    {"name": "ლოგისტიკა/ტრანსპორტი/დისტრიბუცია", "cid": 5},
    {"name": "მშენებლობა/რემონტი", "cid": 11},
    {"name": "დასუფთავება", "cid": 16},
    {"name": "დაცვა/უსაფრთხოება", "cid": 17},
    {"name": "IT/პროგრამირება", "cid": 6},
    {"name": "მედია/გამომცემლობა", "cid": 13},
    {"name": "განათლება", "cid": 12},
    {"name": "სამართალი", "cid": 7},
    {"name": "მედიცინა/ფარმაცია", "cid": 8},
    {"name": "სილამაზე/მოდა", "cid": 14},
    {"name": "კვება", "cid": 10},
    {"name": "სხვა", "cid": 9},
]

LISTING_URL = (
    "https://www.jobs.ge/?page={page}&q=&cid={cid}&lid=0&jid=0"
    "&in_title=0&has_salary=0&is_ge=0&for_scroll=yes"
)

REQUEST_DELAY = 5  # seconds; respects jobs.ge's robots.txt crawl-delay


def print_logo():
    print(
        r"""
      __   __   __      __   __   __        __   __   __
   | /  \ |__) /__`    /__` /  ` |__)  /\  |__) |__  |__)
\__/ \__/ |__) .__/    .__/ \__, |  \ /~~\ |    |___ |  \


github: https://github.com/DarkLordGeo
        """
    )


def fetch_listing_rows(cid, delay=REQUEST_DELAY):
    """Fetch every listing row (<tr>) across all pages for a category id."""
    rows = []
    page = 0
    while True:
        page += 1
        url = LISTING_URL.format(page=page, cid=cid)
        req = requests.get(url, timeout=30)
        soup = BeautifulSoup(req.text, "html.parser")
        page_rows = soup.find_all("tr")
        rows.extend(page_rows)
        print(f"Accessed page {page} ({len(page_rows)} rows)")
        # if there is less than 300 listing on page stop accessing it
        if len(page_rows) < 300:
            print(f"End of job listing was found on page {page}")
            break
        time.sleep(delay)
    return rows


def parse_job(row, delay=REQUEST_DELAY):
    """Fetch and parse a single job's description page.

    Returns a dict describing the job, or None if the row isn't a real
    listing row. `job_url` is always present when a dict is returned, so
    it can be used as a stable identifier for diffing between scrapes.
    """
    tds = row.find_all("td")
    job_anchor = row.find("a")
    if not job_anchor or not job_anchor.get("href"):
        return None

    job_link = job_anchor.get("href")[1:]  # strip leading '/'
    job_url = f"https://www.jobs.{job_link}"

    if len(tds) < 6:
        return None
    data = [td.get_text(strip=True) for td in tds if td.get_text(strip=True)]
    if len(data) < 4:
        return None

    job = {
        "job_position": data[0],
        "job_company": data[1],
        "job_start_date": data[2],
        "job_expire_date": data[3],
        "job_url": job_url,
    }

    try:
        desc_resp = requests.get(job_url, timeout=30)
        time.sleep(delay)
    except requests.RequestException as e:
        print(f"failed to fetch {job_url}: {e}")
        return job

    if desc_resp.status_code != 200:
        print(f"failed to fetch {job_url}: status {desc_resp.status_code}")
        return job

    soup = BeautifulSoup(desc_resp.text, "html.parser")
    dtable = soup.find("table", {"class": "dtable"})
    if not dtable:
        return job

    anchors = dtable.find_all("a")

    if len(anchors) == 2 and anchors[-1].text == "აქ":
        # jobs.ge shows a plain "apply here" link instead of an inline description
        job["job_apply_link"] = anchors[-1].get("href")
    elif len(anchors) == 2 and anchors[-1].text == "ინგლისურ ენაზე":
        # listing points to a separate English-language version of the posting
        en_href = anchors[-1].get("href")
        try:
            en_resp = requests.get(f"https://jobs.ge/{en_href}", timeout=30)
            time.sleep(delay)
            if en_resp.status_code == 200:
                en_soup = BeautifulSoup(en_resp.text, "html.parser")
                en_dtable = en_soup.find("table", class_="dtable")
                en_rows = en_dtable.find_all("tr") if en_dtable else []
                if en_rows:
                    job["job_description"] = en_rows[-1].text
            else:
                print(f"failed to fetch {en_href}: status {en_resp.status_code}")
        except requests.RequestException as e:
            print(f"failed to fetch {en_href}: {e}")
    else:
        desc_rows = dtable.find_all("tr")
        if desc_rows:
            job["job_description"] = desc_rows[-1].text

    return job


def scrape_category(index, delay=REQUEST_DELAY):
    """Scrape every listing in CATEGORIES[index].

    Returns a dict keyed by job_url (a stable identifier suitable for
    diffing between runs), mapping to the parsed job dict.
    """
    category = CATEGORIES[index]
    print(f"Scraping category: {category['name']}")
    rows = fetch_listing_rows(category["cid"], delay=delay)

    jobs = {}
    for row in rows:
        job = parse_job(row, delay=delay)
        if job:
            jobs[job["job_url"]] = job
    print(f"jobs scraped: {len(jobs)}")
    return jobs


def _print_categories():
    for i, c in enumerate(CATEGORIES):
        print(i, c["name"])


def _interactive_main():
    print_logo()
    _print_categories()
    choice = int(input("Choose which category you want to scrape: "))
    jobs = scrape_category(choice)
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump({"jobs": jobs}, f, ensure_ascii=False, indent=4)
    print("Saved to jobs.json")


def main():
    parser = argparse.ArgumentParser(description="Scrape job listings from jobs.ge")
    parser.add_argument(
        "--category",
        type=int,
        help="Category index (see --list-categories). Skips the interactive prompt.",
    )
    parser.add_argument(
        "--list-categories", action="store_true", help="Print category indices and exit."
    )
    parser.add_argument(
        "--output", default="jobs.json", help="Output JSON path (default: jobs.json)"
    )
    parser.add_argument(
        "--delay", type=float, default=REQUEST_DELAY, help="Delay between requests in seconds"
    )
    args = parser.parse_args()

    if args.list_categories:
        _print_categories()
        return

    if args.category is None:
        _interactive_main()
        return

    print_logo()
    jobs = scrape_category(args.category, delay=args.delay)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"jobs": jobs}, f, ensure_ascii=False, indent=4)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
