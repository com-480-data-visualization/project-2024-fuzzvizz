import os
import glob
import scrapy
import json
import requests

from scrapy.crawler import CrawlerProcess


class MozillaSpider(scrapy.Spider):

    name = __file__
    max_id = 10000000

    def start_requests(self):
        all = set(range(390000, self.max_id + 1))
        downloaded = set(
            map(
                lambda x: int(os.path.basename(x[0:-5])), glob.glob("crawled/mozilla/*")
            )
        )

        urls = [
            f"https://bugzilla.mozilla.org/show_bug.cgi?id={i}"
            for i in all - downloaded
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        bug = {}

        match = response.xpath('string(//span[@id="field-value-bug_id"])').re(
            "Bug (\d+)\s+(\(CVE-.+\))?"
        )
        if len(match) == 1:
            id = match[0]
            bug["id"] = id
        elif len(match) == 2:
            id, cve = match
            bug["id"], bug["cve"] = id, cve
        else:
            return

        # Extracting basic bug details
        for field in response.xpath('//span[starts-with(@id, "field-value-")]/../..'):
            try:
                name = field.css(".name").xpath("string(.)").get().strip().lower()
                value = field.css(".value").xpath("string(.)").get().strip().lower()
                bug[name] = value
            except:
                pass

        if (
            "component:" not in bug.keys()
            or "javascript engine" not in bug["component:"]
        ):
            print("skip")
            return

        # Extracting comments
        comments = []
        for comment in response.css("div.change-set"):
            try:
                author = comment.css(".change-author").xpath("string(.)").get().strip()
                time = comment.css(".rel-time").xpath("string(.)").get().strip()
                text = comment.css(".comment-text").xpath("string(.)").get().strip()
                comments.append({"author": author, "time": time, "text": text})
            except:
                pass

        # Extract and download attachments
        attachments = []
        for attachment in response.css("table#attachments div.attach-desc"):
            href = attachment.xpath("a/@href").get()
            name = attachment.xpath("string(a)").get().strip()
            url = response.urljoin(href)
            content = requests.get(url).content.decode("utf-8", "backslashreplace")
            attachments.append(
                {
                    "name": name,
                    "url": url,
                    "content": content,
                }
            )

        bug["comments"] = comments
        bug["attachments"] = attachments

        # Save data to file
        with open("crawled/mozilla/" + str(id) + ".json", "w") as f:
            json.dump(bug, f)


process = CrawlerProcess(
    settings={
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "DOWNLOAD_DELAY": 1,
    }
)

process.crawl(MozillaSpider)
process.start()
