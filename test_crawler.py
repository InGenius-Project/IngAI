import json
import time

import requests
import tool
from bs4 import BeautifulSoup

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
headers = {"User-Agent": userAgent}


baseURL = "https://guide.104.com.tw/salary/topic?subject=jobsratio&type=worker&cat=all"


jobs_data = []

while jobs_data == []:
    driver = tool.SeleniumDriver()
    protal = driver.get(url=baseURL)

    page_source = driver.get_content()
    time.sleep(3)
    soup = BeautifulSoup(page_source, "html.parser")

    jobs = soup.findAll("div", class_="info")

    for job in jobs:

        job_info = {}

        paragraphs = job.findAll("p")
        job_info["職業"] = paragraphs[0].text
        print(job_info)
        print()

        for p in paragraphs[1:]:

            text = p.text

            key, value = text.split("：")

            job_info[key] = value

        jobs_data.append(job_info)


print(jobs_data)
data_list = []


for job in jobs_data:
    job_dict = {"職業": job["職業"], "月均薪": job["月均薪"]}
    data_list.append(job_dict)

json_data = json.dumps(data_list, ensure_ascii=False, indent=4)

print(json_data)

with open("job_data.json", "w", encoding="utf-8") as f:
    f.write(json_data)

print("JSON 文件已保存为 job_data.json")
