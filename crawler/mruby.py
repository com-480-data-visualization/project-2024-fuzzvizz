import requests, scrapy, json, glob, os

from scrapy.crawler import CrawlerProcess


class GitHubSpider(scrapy.Spider):
    list_url = "https://api.github.com/repos/{}/issues"
    content_url = "https://api.github.com/repos/{}/issues/{}"
    name = __file__
    max_id = 100000
    repo_name = "mruby/mruby"

    def start_requests(self):
        crawled = [
            int(os.path.splitext(os.path.basename(f))[0])
            for f in glob.glob("crawled/mruby/*")
            if os.path.splitext(os.path.basename(f))[0].isdigit()
        ]

        with open("github_token", "r") as f:
            self.token = f.read().strip()
            self.headers = {"Authorization": f"Bearer {self.token}"}

        try:
            with open("mruby_issues.json", "r") as f:
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

            with open("mruby_issues.json", "w") as f:
                json.dump(issues, f)

        issues = set(issues) - set(crawled)
        for i in issues:
            url = self.content_url.format(self.repo_name, i)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        response = response.json()

        response = response | {
            "comments": requests.get(
                response["comments_url"], headers=self.headers
            ).json(),
            # "attachments": files,
        }

        with open(f"crawled/mruby/{response['number']}.json", "w") as f:
            json.dump(response, f)

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
        "DOWNLOAD_DELAY": 1,
    }
)

process.crawl(GitHubSpider)
process.start()
