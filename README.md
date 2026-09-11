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

### Using your own fork

GitHub never copies secrets into a fork, so forking this repo does **not**
give anyone access to the original bot's token, and running the fork's
own scheduled workflows never touches the upstream repo's subscribers or
snapshots — each fork is fully independent. To run your own instance:

1. Fork the repo.
2. Open your fork's **Actions** tab and click **"I understand my
   workflows, go ahead and enable them"** — GitHub disables Actions on
   forks by default.
3. Create your own bot with [@BotFather](https://t.me/BotFather) and copy
   its token.
4. In your fork, go to **Settings → Secrets and variables → Actions →
   New repository secret**, name it `TELEGRAM_BOT_TOKEN`, and paste your
   token.
5. That's it — the workflows pick it up on their next scheduled run (or
   trigger one immediately from the Actions tab). Your fork builds up its
   own `data/subscribers.json` and `data/snapshots/`, separate from
   upstream.

If Actions are enabled but the secret hasn't been added yet, both
workflows detect that and skip with a warning instead of failing.

### Keeping your fork up to date

Once your fork's workflows have run at least once, they'll have
committed to `data/subscribers.json`/`data/snapshots/`, which puts your
fork's `main` branch **ahead** of the upstream repo. That's expected —
but it also means GitHub's one-click "Sync fork" button (top of your
fork's page) may stop offering a plain fast-forward and instead show
"Discard commits" — **don't use that**, it deletes your subscriber data.

Pull in upstream changes with a real merge instead, which is safe here
because your commits only ever touch `data/`, while upstream changes only
ever touch code/docs — the two essentially never conflict:

```
git remote add upstream https://github.com/DarkLordGeo/JobsGeScraper.git   # one-time
git fetch upstream
git merge upstream/main
git push origin main
```

Do this whenever you want the latest scraper/bot code, on whatever
cadence suits you — there's no automatic sync, from either side.

Two things to keep in mind either way (not fork-specific, just how GitHub
Actions works): scheduled workflows only fire from the repository's
**default branch**, and GitHub auto-disables `schedule` triggers after
**60 days** with no commits to the repo — push anything to re-enable them.


### Contributions

Any type of contribution is welcome.

### Screenshots

![screenshot: ](https://github.com/DarkLordGeo/JobsGeScraper/blob/main/imgs/image_1.png)
![screenshot:](https://github.com/DarkLordGeo/JobsGeScraper/blob/main/imgs/image_2.png)
![screenshot:](https://github.com/DarkLordGeo/JobsGeScraper/blob/main/imgs/image_3.png)



