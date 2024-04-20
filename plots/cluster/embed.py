import os
import glob
import json
import voyageai
import time

from multiprocessing import Pool

tmpl = """
## Bug summary
{}

## Reproducer
{}
"""


with open("voyage_api_key", "r") as f:
    api_key = f.read().strip()

vo = voyageai.Client(api_key=api_key)


target = "php"
extracted = set([os.path.basename(p) for p in glob.glob(f"embeddings/{target}/*.json")])
remaining = [
    p
    for p in glob.glob(f"extracted/{target}/*.json")
    if os.path.basename(p) not in extracted
]

os.makedirs(f"embeddings/{target}", exist_ok=True)


def embed(p):

    name = os.path.basename(p)

    try:
        with open(p) as f:
            extracted = json.load(f)

        if extracted["reproducer"] is None or extracted["reproducer"].startswith("N/A"):
            return

        report = tmpl.format(extracted["summary"], extracted["reproducer"])
        embeddings = vo.embed(
            [report],
            model="voyage-code-2",
            input_type="document",
        ).embeddings[0]

        cjson = {"id": extracted["id"], "embeddings": embeddings}

        print(cjson)

        with open(f"embeddings/{target}/{name}", "w") as f:
            json.dump(cjson, f)

    except Exception as e:
        print(e)
        with open(f"embeddings/{target}/{name}", "w") as f:
            json.dump(
                {"id": None, "report": None, "summary": None, "reproducer": None}, f
            )


with Pool(1) as pool:
    time.sleep(1)
    pool.map(embed, remaining)
