import json
import scrapy
import requests
import glob
import os

from scrapy.crawler import CrawlerProcess


class GCCSpider(scrapy.Spider):
    name = __file__
    max_id = 113616
    base_url = "https://gcc.gnu.org/bugzilla"

    def start_requests(self):
        all = set(range(1, self.max_id + 1))
        downloaded = set(
            map(lambda x: int(os.path.basename(x[0:-5])), glob.glob("crawled/gcc/*"))
        )

        urls = [
            f"{self.base_url}/show_bug.cgi?id={i}" for i in all.difference(downloaded)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Extract basic details like title, bug id, status, product, etc.
        id, title = response.css("title::text").re(r"(\d+) \u2013 (.+)")
        labels = {
            label.xpath("string(.)")
            .get()
            .strip()
            .replace(":", "")
            .lower(): label.xpath("string(following-sibling::td)")
            .get()
            .strip()
            for label in response.css(".bz_show_bug_column th.field_label")
        }

        # Extract comments
        comments = [
            {
                "author": comment.css(".bz_comment_user")
                .xpath("string(.)")
                .get()
                .strip(),
                "time": comment.css(".bz_comment_time")
                .xpath("string(.)")
                .get()
                .strip(),
                "text": comment.css(".bz_comment_text")
                .xpath("string(.)")
                .get()
                .strip(),
            }
            for comment in response.css(".bz_comment")
        ]

        # Extract and download attachments
        attachments = []
        for attachment in response.css("#attachment_table tr").xpath(".//b/.."):
            href = attachment.xpath("@href").get()
            name = attachment.xpath("string(b)").get().strip()
            url = response.urljoin(href)
            content = requests.get(url).content.decode("utf-8", "backslashreplace")
            attachments.append(
                {
                    "name": name,
                    "url": url,
                    "content": content,
                }
            )

        bug = labels | {
            "id": id,
            "title": title,
            "comments": comments,
            "attachments": attachments,
        }

        with open("crawled/gcc/" + str(id) + ".json", "w") as f:
            f.write(json.dumps(bug))

        # print(bug_details)


process = CrawlerProcess(
    settings={
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
)

process.crawl(GCCSpider)
process.start()
