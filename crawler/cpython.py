import requests
import scrapy
import json
import re
import glob
import os

from scrapy.crawler import CrawlerProcess


class GitHubSpider(scrapy.Spider):
    list_url = "https://api.github.com/repos/{}/issues"
    content_url = "https://api.github.com/repos/{}/issues/{}"
    name = __file__
    max_id = 100000
    repo_name = "python/cpython"

    def start_requests(self):
        crawled = []
        for f in glob.glob("crawled/cpython/*"):
            try:
                name = os.path.basename(f)
                noext = os.path.splitext(name)[0]
                crawled.append(int(noext))
            except:
                pass

        with open("github_token", "r") as f:
            self.token = f.read().strip()
            self.headers = {"Authorization": f"Bearer {self.token}"}

        try:
            with open("cpython_issues.json", "r") as f:
                issues = json.load(f)
        except:
            issues = []
            p = 1
            while True:
                l = self.list_issues(p)
                if len(l) == 0:
                    break

                for response in l:
                    issues.append(response["number"])

                p += 1

            with open("cpython_issues.json", "w") as f:
                json.dump(issues, f)

        issues = set(issues) - set(crawled)
        for i in issues:
            url = self.content_url.format(self.repo_name, i)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        response = response.json()

        id = response["number"]
        body = response["body"] or ""
        comments_url = response["comments_url"]
        comments = requests.get(comments_url, headers=self.headers).json()

        files = []
        reg = r"\[([^\[\]]+)\]\((https://bugs.python.org/file\d+/\S+) [^()]*\)"
        for m in re.findall(reg, body):
            name, url = m
            content = requests.get(url).content.decode("utf-8", "backslashreplace")
            files.append(
                {
                    "name": name,
                    "url": url,
                    "content": content,
                }
            )

        response = response | {
            "comments": comments,
            "attachments": files,
        }

        with open(f"crawled/cpython/{id}.json", "w") as f:
            json.dump(response, f)

    def get_issue_content(self, repo, issue_number):
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def list_issues(self, page=1):
        url = f"https://api.github.com/repos/{self.repo_name}/issues"
        params = {
            "state": "all",
            "sort": "created",
            "direction": "asc",
            "per_page": 100,
            "page": page,
        }
        response = requests.get(url, params=params, headers=self.headers)
        return response.json()


process = CrawlerProcess(
    settings={
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "DOWNLOAD_DELAY": 2,
    }
)

process.crawl(GitHubSpider)
process.start()
