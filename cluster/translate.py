import re
import json
import argparse
import pydantic

from common import *
from time import sleep
from multiprocessing import Pool

with open("translate.prompt.md", "r") as p:
    prompt = p.read()

class Result(pydantic.BaseModel):
    explanation: str
    reproducer: str | None


def translate(j, src, tgt):
    content = prompt.format(src, tgt, j["summary"], j["reproducer"])

    print(content)

    response = prompt_single(
        content=content,
        schema=Result.model_json_schema(),
        model="gpt4",
    )

    print(response.choices[0].message.content)

    return response.choices[0].message.content

def translate_dump(p):
    name = os.path.basename(p)
    out = f"translated/{src}-{tgt}/{name}"

    print(out)
    if os.path.exists(out):
        return

    with open(p, "r") as f, open(out, "w") as w:
        j = json.load(f)
        repro = j["reproducer"]

        if repro:
            response = translate(j, src, tgt)
            json.dump(response, w)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("target")
    args = parser.parse_args()

    src = args.source
    tgt = args.target

    os.makedirs(f"translated/{src}-{tgt}/", exist_ok=True)

    work = list(glob.glob(f"extracted/{src}/*.json"))
    with Pool(8) as pool:
        pool.map(translate_dump, work)
