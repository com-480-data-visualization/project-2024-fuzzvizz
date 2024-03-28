import re
import os
import glob
import scrapy
import json

from scrapy.crawler import CrawlerProcess


class PHPSpider(scrapy.Spider):

    name = __file__
    max_id = 113616
    base_url = "https://bugs.php.net"

    def start_requests(self):
        all = set(range(1, self.max_id + 1))
        downloaded = set(
            map(lambda x: int(os.path.basename(x[0:-5])), glob.glob("crawled/php/*"))
        )

        urls = [
            f"https://bugs.php.net/bug.php?id={i}" for i in all.difference(downloaded)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        bug = {}

        # Extracting basic bug details
        for th in response.xpath('//table[@id="details"]//tr/th'):
            key = th.xpath("string(.)").get()
            value = th.xpath("string(following-sibling::td)").get()

            if m := re.match(r"(\w+).#(\d+)", key):
                bug["type"] = m.group(1)
                bug["id"] = m.group(2)
                bug["title"] = value
            else:
                bug[key.lower()] = value

        if not "id" in bug.keys():
            return

        # Extracting comments
        comments = []
        for comment in response.css(".comment"):
            time, author = comment.xpath("string(strong)").re(r"\[(.+)\] (.*)")
            text = comment.xpath("string(pre)").get()
            comments.append(
                {
                    "author": author,
                    "time": time,
                    "text": text,
                }
            )

        bug["comments"] = comments

        # Save data to file
        with open("crawled/php/" + bug["id"] + ".json", "w") as f:
            json.dump(bug, f)


process = CrawlerProcess(
    settings={
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
)

process.crawl(PHPSpider)
process.start()
