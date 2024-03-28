import os
import glob
import scrapy
import json
import requests

from scrapy.crawler import CrawlerProcess


class RubySpider(scrapy.Spider):
    name = __file__
    max_id = 113616

    def start_requests(self):
        all = set(range(37000, self.max_id + 1))
        downloaded = set(
            map(lambda x: int(os.path.basename(x[0:-5])), glob.glob("crawled/ruby/*"))
        )

        urls = [
            f"https://bugs.ruby-lang.org/issues/{i}" for i in all.difference(downloaded)
        ]
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                cookies={
                    "_redmine_session": "MUdKS29wM0d6aEg0NkVpbVZkQmtONTZRekZNMmtoa013MjVFMFd2UC9lckxpdE1KekkzSVpJdytwK2JvVExlQ2lrNWJVZXVreFZ6Vll3WjhXT2g4UUUrS08yMk1WOEI1bmhmUjI3ajU5MlpPUFcreGJNNnlYeW5RZ296S3ZtOG1kS3BHUm8wa1hkYTYyUisvKzFqQ0tQaW0vYU1PNGxrT2Z3eE51NnliNk1wQ05VWXNoUXE1am83SGpUaURLZFhHdm9mVDVZclFZMkUxaStySmwyeWVwUmo1RFJSdkVHZTBpMmh4WE5TR00yTTVqRTBOUkZTZHBhQlRrMGp5Y1JEVldLL2JOUWd0YWJHUXBUblpBMlozb3FDNkRRMEpZbndEYngrcTNkYzNFR3prL0RZYnpWblZDQTNiMmNneGFLREctLTdBZm5mUmpDaUY5aWVuVXI2UXNpdmc9PQ%3D%3D--299dffb397c9a19be6fe92d48019aed7eb259060"
                },
            )

    def parse(self, response):
        bug = {}

        ty, id = response.css(".inline-flex").re(r"(\w+) #(\d+)")
        description = response.css(".description .wiki").xpath("string(.)").get()
        title = response.css(".subject h3::text").get()
        author = response.css(".author .user::text").get()
        bug["id"] = id
        bug["type"] = ty
        bug["title"] = title
        bug["author"] = author
        bug["description"] = description

        # Extracting basic bug details
        for field in response.css(".attribute"):
            name = field.css(".label").xpath("string(.)").get().strip().lower()
            value = field.css(".value").xpath("string(.)").get().strip().lower()
            bug[name] = value

        # Extracting comments
        comments = []
        for comment in response.css("#history .note"):
            try:
                author = comment.css(".user.active").xpath("string(.)").get().strip()
                time = (
                    comment.css(".note-header")
                    .xpath(".//a[@title and @href]/@title")
                    .get()
                    .strip()
                )
                text = comment.css(".wiki").xpath("string(.)").get().strip()
                comments.append({"author": author, "time": time, "text": text})
            except:
                pass
        bug["comments"] = comments

        attachments = []
        for attachment in response.css("div.attachments tr"):
            name = attachment.css(".icon-attachment::text").get()
            href = attachment.css(".icon-download").xpath("./@href").get()
            url = response.urljoin(href)
            content = requests.get(url).content.decode("utf-8", "backslashreplace")
            attachments.append(
                {
                    "name": name,
                    "url": url,
                    "content": content,
                }
            )

        bug["attachments"] = attachments

        # Save data to file
        with open("crawled/ruby/" + str(id) + ".json", "w") as f:
            json.dump(bug, f)


process = CrawlerProcess(
    settings={
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "DOWNLOAD_DELAY": 1,
    }
)

process.crawl(RubySpider)
process.start()
