from bs4 import BeautifulSoup
import requests
import json
import time



def main():
    def logo():
            print(
            f"""
        _       _           ____   ____ ____      _    ____  _____ ____  
        | | ___ | |__  ___  / ___| / ___|  _ \    / \  |  _ \| ____|  _ \ 
    _  | |/ _ \| '_ \/ __| \___ \| |   | |_) |  / _ \ | |_) |  _| | |_) |
    | |_| | (_) | |_) \__ \  ___) | |___|  _ <  / ___ \|  __/| |___|  _ < 
    \___/ \___/|_.__/|___/ |____/ \____|_| \_\/_/   \_\_|   |_____|_| \_\ 
                                        
        
        github: https://github.com/DarkLordGeo
        """
        )

    logo()

    def userInput():
            user_choices = [
                "ადმინისტრაცია/მენეჯმენტი",
                "ფინანსები/სტატისტიკა",
                "გაყიდვები",
                "PR/მარკეტინგი",
                "ზოგადი ტექნიკური პერსონალი",
                "ლოგისტიკა/ტრანსპორტი/დისტრიბუცია",
                "მშენებლობა/რემონტი",
                "დასუფთავება",
                "დაცვა/უსაფრთხოება",
                "IT/პროგრამირება",
                "მედია/გამომცემლობა",
                "განათლება",
                "სამართალი",
                "მედიცინა/ფარმაცია",
                "სილამაზე/მოდა",
                "კვება",
                "სხვა",
            ]

            job_links = [
                "https://www.jobs.ge/?page={page}&q=&cid=1&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=3&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=2&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=4&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=18&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=5&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=11&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=16&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=17&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=6&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=13&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=12&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=7&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=8&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=14&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=10&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
                "https://www.jobs.ge/?page={page}&q=&cid=9&lid=0&jid=0&in_title=0&has_salary=0&is_ge=0&for_scroll=yes",
            ]
            for index, x in enumerate(user_choices):
                print(index, x)
            user_input = int(input("Choose which category you want to scrape: "))
            return job_links[user_input]

    template_url = userInput()
    get_all_pages = False
    i = 0
    data = []

    while not get_all_pages:
            i += 1
            url = template_url.format(page=i)
            req = requests.get(url)
            soup = BeautifulSoup(req.text, "html.parser")
            rows = soup.find_all("tr")
            data.extend(rows)
            # if there is less than 300 listing on page stop accessing it
            print(f"Accessed page {i}")
            if len(rows) < 300:
                print(f"End of job listing was found on {i}, Starting to store data...")
                get_all_pages = True

            time.sleep(5)
    print(f"url: {url}")
    def scrapJobsGe(rows):
        all_jobs = {}
        for index, row in enumerate(rows, start=0):
                # loop over html table , start at 0, keep track of index and rows
                tds = row.find_all("td")
                # find all table data

                job_anchor = row.find("a")
                # get anchor of current job , find method finds first occurance of anchor

                job_anchors = []
                # define list to store job anchors

                if job_anchor:
                    # if job link exists than we should start scraping

                    job_anchors.append(job_anchor.get("href")[1:])

                    # appending job_anchor href attribute skipping 0

                    for job_link in job_anchors:

                        job_desc_url = requests.get(f"https://www.jobs.{job_link}")
                        # making requests to each job description url by formatting string, having it in loop makes it to try every possible appended element to job_anchor and passing job_link to request.get

                        job_desc_text = job_desc_url.text
                        # getting text

                        soup = BeautifulSoup(job_desc_text, "html.parser")
                        # parsing job description

                        job_desc_anchor = soup.find("table", {"class": "dtable"}).find_all(
                            "a"
                        )

                        # searching for html table with class of dtable and searching for all anchors

                        if len(job_desc_anchor) == 2 and job_desc_anchor[-1].text == "აქ":
                            # costum logic for existing anchors on webpage. In this situation we aim for 'აქ' text

                            for anchor in job_desc_anchor:
                                anchor_here = anchor.get("href")
                                if len(tds) < 6:
                                    continue
                                data = [
                                    td.get_text(strip=True)
                                    for td in tds
                                    if td.get_text(strip=True)
                                ]
                                if len(data) < 4:
                                    continue
                                all_jobs[f"job_{index}"] = {
                                    "job_position": data[0],
                                    "job_company": data[1],
                                    "job_start_date": data[2],
                                    "job_expire_date": data[3],
                                    "job_link": anchor_here,
                                    # "job_url":job_desc_url
                                }
                                # job data dictionary
                                job_data = {"jobs": all_jobs}

                                with open("jobs.json", "w", encoding="utf-8") as write_file:
                                    json.dump(
                                        job_data,
                                        write_file,
                                        ensure_ascii=False,
                                        indent=4,
                                    )
                                    # print(len(all_jobs))
                                # opening jobs.json file.
                                # using json dump

                        # english text vacancies

                        if (
                            len(job_desc_anchor) == 2
                            and job_desc_anchor[-1].text == "ინგლისურ ენაზე"
                        ):
                            for english_anchor in job_desc_anchor:
                                english_anchor_here = english_anchor.get("href")
                                # print(english_anchor_here)

                                try:
                                    english_job_desc_url = requests.get(
                                        f"https://jobs.ge/{english_anchor_here}"
                                    )
                                    english_job_desc_url_text = english_job_desc_url.text

                                    if english_job_desc_url.status_code != 200:
                                        print("failed to fetch")
                                        continue

                                    englishSoup = BeautifulSoup(
                                        english_job_desc_url_text, "html.parser"
                                    )
                                    english_desc_last_tr = englishSoup.find(
                                        "table", class_="dtable"
                                    ).find_all("tr")

                                    if english_desc_last_tr:
                                        english_desc_json = english_desc_last_tr[-1].text

                                        if len(tds) < 6:
                                            continue
                                        data = [
                                            td.get_text(strip=True)
                                            for td in tds
                                            if td.get_text(strip=True)
                                        ]
                                        if len(data) < 4:
                                            continue

                                        all_jobs[f"job_{index}"] = {
                                            "job_position": data[0],
                                            "job_company": data[1],
                                            "job_start_date": data[2],
                                            "job_expire_date": data[3],
                                            "job_description": english_desc_json,
                                        }
                                        job_data = {"jobs": all_jobs}
                                        with open(
                                            "jobs.json", "w", encoding="utf-8"
                                        ) as write_file:
                                            json.dump(
                                                job_data,
                                                write_file,
                                                ensure_ascii=False,
                                                indent=4,
                                            )

                                    else:
                                        print(
                                            "no tables with dtable class found on this page"
                                        )

                                except Exception as e:
                                    print(e)

                        else:
                            job_desc_last_tr = soup.find(
                                "table", {"class": "dtable"}
                            ).find_all("tr")
                            job_desc_json = job_desc_last_tr[-1].text

                            if len(tds) < 6:
                                continue

                            data = [
                                td.get_text(strip=True)
                                for td in tds
                                if td.get_text(strip=True)
                            ]

                            if len(data) < 4:
                                continue

                            all_jobs[f"job_{index}"] = {
                                "job_position": data[0],
                                "job_company": data[1],
                                "job_start_date": data[2],
                                "job_expire_date": data[3],
                                "job_description": job_desc_json,
                                "job_url": f"https://www.jobs.{job_link}",
                            }
                            job_data = {"jobs": all_jobs}
                            print("jobs scraped: ", len(all_jobs))
                            with open("jobs.json", "w", encoding="utf-8") as write_file:
                                json.dump(
                                    job_data, write_file, ensure_ascii=False, indent=4
                                )

    scrapJobsGe(data)


if __name__ == '__main__':
    main()