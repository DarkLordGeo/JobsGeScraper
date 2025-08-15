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

pip install requirements.txt

python scraper.py
```
### Version
Python 3.12.6


### Contributions

Any type of contribution is welcome.



