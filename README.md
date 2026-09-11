# JobsGeScraper

JobsGeScraper is a simple Python-based scraper designed to collect job listings from Jobs.ge. It uses BeautifulSoup, requests, and json to fetch and process data.

This scraper focuses on retrieving all job listings across the available categories on the Jobs.ge website. To respect the website’s rules, it automatically delays requests by 5 seconds, following the instructions in Jobs.ge’s robots.txt 

## Features:

- Scrapes all available job categories.

- Stores collected data in a structured format (JSON).

- Respects crawl-delay from the website.



## Run the scraper:
```
git clone https://github.com/DarkLordGeo/JobsGeScraper.git

cd JobsGeScraper

pip install -r requirements.txt

python scraper.py
```

Non-interactive one-off run (skips the category prompt):
```
python scraper.py --list-categories
python scraper.py --category 9 --output it_jobs.json
```

### Version
Python 3.12.6

## Telegram notifications

Subscribers can pick which job categories they want to be notified
about, straight from Telegram — no config file editing required.

**Bot commands:**
| Command | What it does |
|---|---|
| `/categories` | List all job categories with their index |
| `/subscribe <n>` | Subscribe to category `n` |
| `/unsubscribe <n>` | Unsubscribe from category `n` |
| `/mysubs` | List your current subscriptions |

**Setup (repo owner):**
1. Create a bot with [@BotFather](https://t.me/BotFather) on Telegram and copy the bot token.
2. Add it as a repository secret: **Settings → Secrets and variables → Actions → New repository secret**, name `TELEGRAM_BOT_TOKEN`.
3. Push to `main` (scheduled workflows only fire from the default branch). Two workflows then run automatically:
   - **`.github/workflows/telegram-bot.yml`** — polls Telegram every 5 minutes for new `/subscribe`-style commands and commits the result to `data/subscribers.json`.
   - **`.github/workflows/notify.yml`** — every 2 hours (tune the cron to taste), scrapes every category that has at least one subscriber, diffs it against the last snapshot in `data/snapshots/`, and messages subscribers about newly-posted jobs. The first run per category just establishes a baseline — nobody gets spammed with every job currently listed.

Both workflows can also be triggered manually from the Actions tab (`workflow_dispatch`).

Note: scraping fetches every job's description page with a 5s delay each
(to respect jobs.ge's `robots.txt` crawl-delay), so a large category can
take a while to scrape — size the notify workflow's schedule accordingly.


### Contributions

Any type of contribution is welcome.

### Screenshots

![screenshot: ](https://github.com/DarkLordGeo/JobsGeScraper/blob/main/imgs/image_1.png)
![screenshot:](https://github.com/DarkLordGeo/JobsGeScraper/blob/main/imgs/image_2.png)
![screenshot:](https://github.com/DarkLordGeo/JobsGeScraper/blob/main/imgs/image_3.png)



