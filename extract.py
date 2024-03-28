import json
import pydantic
import tqdm
import os

from common import *
from multiprocessing import Pool

# acc = pl.DataFrame()

# for p in glob.glob("crawled/{target}/*.json"):
#     with open(p) as f:
#         j = json.load(f)
#         print(j["labels"])
# print(j["body"])
# print(j["comments"])
# df = pl.read_json(f, schema={"body": pl.Utf8, "comments": pl.List(pl.Struct({"body": pl.Utf8}))})
# print(df.columns)
# acc.vstack(df, in_place=True)

# acc.rechunk()

# print(acc.filter(pl.col("comments").is_not_null()))
# print(acc)
# print(pl.scan_ndjson("jsonl/*.json", infer_schema_length=10000).columns)


class Result(pydantic.BaseModel):
    summary: str
    reproducer: str | None


title = "# {}" + "\n"
body = "- {}" + "\n" + "{}" + "\n"
att = "- {}" + "\n" + "{}" + "\n"
with open(os.path.join(workdir, "extract.prompt.md"), "r") as f:
    md = f.read()

target = "php"
remaining = get_remaining("crawled", "extracted", target)
print(len(remaining))

os.makedirs(f"extracted/{target}", exist_ok=True)


def extract_ruby(crawled):
    if not crawled["type"] == "Bug":
        return None

    report = title.format(crawled["title"])
    report += body.format(crawled["author"], crawled["description"])

    if len(crawled["comments"]) > 0:
        report += "## Comments\n"
    for c in crawled["comments"]:
        report += body.format(c["author"], c["text"])

    if len(crawled["attachments"]) > 0:
        report += "## Attachments\n"
    for a in crawled["attachments"]:
        if len(a["content"]) > 8192:
            continue
        report += att.format(a["name"], a["content"])

    return report


def extract_webkit(crawled):
    if not "JavaScriptCore" in crawled["component"]:
        return None

    report = title.format(crawled["title"])

    if len(crawled["comments"]) > 0:
        report += "## Comments\n"
    for c in crawled["comments"]:
        report += body.format(c["author"], c["text"])

    if len(crawled["attachments"]) > 0:
        report += "## Attachments\n"
    for a in crawled["attachments"]:
        if len(a["content"]) > 8192:
            continue
        report += att.format(a["name"], a["content"])


    return report

def extract_php(crawled):
    if not crawled["type"] == "Bug":
        return None

    report = title.format(crawled["title"])

    if len(crawled["comments"]) > 0:
        report += "## Comments\n"
    for c in crawled["comments"]:
        report += body.format(c["author"], c["text"])

    return report


def extract_github(crawled):
    report = title.format(crawled["title"])

    report += body.format(crawled["user"]["login"], crawled["body"])
    if len(crawled["comments"]) > 0:
        report += "## Comments\n"
    for c in crawled["comments"]:
        report += body.format(c["user"]["login"], c["body"])

    return report


def extract(name):
    id = os.path.splitext(name)[0]
    src = os.path.join("crawled", target, name)
    dst = os.path.join("extracted", target, name)

    print(src)
    try:
        with open(src) as f:
            crawled = json.load(f)

        if (report := extract_php(crawled)) is None:
            return

        prompt = md.format(report)
        response = prompt_single(prompt, Result.model_json_schema())
        choice = response.choices[0]
        content = choice.message.content

        print(report)
        print(content)
        result = {"id": id, "report": report} | json.loads(content)
    except Exception as e:
        print(e)
        result = {"id": id, "report": None, "summary": None, "reproducer": None}

    with open(dst, "w") as f:
        json.dump(result, f)


with Pool(10) as pool:
    pool.map(extract, remaining)
