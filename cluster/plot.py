import plotly.express as px
import polars as pl
import numpy as np
import glob
import json
import umap
import os
import hdbscan

from ctfidf import *
from sklearn.feature_extraction.text import CountVectorizer

embeddings = []
ids = []
contents = []
target = "php"

{
    "target": "chakracore",
    "n_neighbors": 10,
    "min_dist": 0.00,
    "min_cluster_size": 20,
    "random_state": 1336,
    "min_samples": 1,
    "n_samples": 1645,
    "n_cluster": 36,
}
{
    "target": "webkit",
    "n_neighbors": 10,
    "min_dist": 0.00,
    "min_cluster_size": 18,
    "random_state": 1332,
    "min_samples": 1,
    "n_samples": 1691,
    "n_cluster": 34,
}
{
    "target": "hermes",
    "n_neighbors": 4,
    "min_dist": 0.0,
    "min_cluster_size": 8,
    "random_state": 1337,
    "min_samples": 3,
    "n_samples": 328,
}
{
    "target": "ruby",
    "n_neighbors": 15,
    "min_dist": 0.0,
    "min_cluster_size": 30,
    "random_state": 1336,
    "min_samples": 1,
    "n_samples": 3271,
    "n_cluster": 39,
}
{
    "target": "mruby",
    "n_neighbors": 12,
    "min_dist": 0.0,
    "min_cluster_size": 20,
    "random_state": 1335,
    "min_samples": 3,
    "n_samples": 2183,
    "n_cluster": 35,
}
{
    "target": "cpython",
    "n_neighbors": 30,
    "min_dist": 0.0,
    "min_cluster_size": 60,
    "random_state": 1337,
    "min_samples": 1,
    "n_samples": 30000,
    "n_cluster": 100,
}
{
    "target": "micropython",
    "n_neighbors": 14,
    "min_dist": 0.0,
    "min_cluster_size": 24,
    "random_state": 1337,
    "min_samples": 1,
    "n_samples": 2621,
    "n_cluster": 41,
}
{
    "target": "luajit",
    "n_neighbors": 4,
    "min_dist": 0.0,
    "min_cluster_size": 8,
    "random_state": 1337,
    "min_samples": 3,
    "n_samples": 363,
    "n_cluster": 20,
}
{
    "target": "php",
    "n_neighbors": 40,
    "min_dist": 0.0,
    "min_cluster_size": 80,
    "random_state": 1335,
    "min_samples": 1,
    "n_samples": 30060,
    "n_cluster": 114,
}


for p in glob.glob(f"embeddings/{target}/*.json"):
    with open(p, "r") as f:
        j = json.load(f)
    print(p)

    df = pl.read_json(p)
    embeddings.append(j["embeddings"])
    ids.append(j["id"])

    try:
        name = os.path.basename(p)
        with open(f"extracted/{target}/{name}", "r") as f:
            e = json.load(f)
        content = (
            e["summary"].replace(". ", ".\n") + "\n----\n" + e["reproducer"]
        ).replace("\n", "<br>")
    except:
        content = ""
    contents.append(content)


arr = np.array(embeddings)

reducer = umap.UMAP(n_neighbors=40, random_state=1335, min_dist=0.0)
reduced = reducer.fit_transform(embeddings)

cluster = hdbscan.HDBSCAN(min_cluster_size=80, min_samples=1)
labels = cluster.fit(reduced).labels_

x = reduced[:, 0]
y = reduced[:, 1]

df = pl.from_dict(
    {
        "x": x,
        "y": y,
        "id": ids,
        "label": labels,
        "content": contents,
    }
)

labelg, concat = (
    df.group_by("label")
    .agg(pl.col("content").str.concat("\n"))
    .select(["label", "content"])
    .get_columns()
)
vectorizer = CountVectorizer(token_pattern=r"[^\W\d_]{3,}", stop_words="english").fit(
    concat
)
counts = vectorizer.transform(concat)
words = vectorizer.get_feature_names_out()
ctf = ClassTfidfTransformer(reduce_frequent_words=True).fit_transform(counts).toarray()
topics = [" ".join([words[i] for i in r.argsort()[-4:]][::-1]) for r in ctf]
mapping = dict(zip(labelg, topics))

df = df.with_columns([pl.col("label").map_dict(mapping).alias("topic")])

print(len(concat))
print(topics)
print(counts.shape, counts)
print(ctf.shape, ctf)
print(x.shape, y.shape, labels.shape, reduced.shape, arr.shape)

fig = px.scatter(
    df.to_dict(),
    x="x",
    y="y",
    color="topic",
    hover_data=["id", "label", "topic", "content"],
)
fig.show()
fig.write_html(f"{target}.html")
