import git
import pandas as pd
import math
import os
import plotly.graph_objs as go
from tqdm import tqdm


def main(git_dir, log_scale=False):
    git_graph(
        git_dir=git_dir,
        log_scale=log_scale
    )


def git_graph(
    git_dir,
    log_scale=False,
):
    git_dir, repo = get_git_repo(git_dir)
    commits = fetch_commits(repo)  # this might take a long time

    plot_total_lines(
        commits=commits,
        git_dir=git_dir,
        log_scale=log_scale,
    )


def get_git_repo(git_dir):
    git_dir = git_dir.strip('"').strip("'")
    repo = git.repo.Repo(git_dir)
    return git_dir, repo


def fetch_commits(repo):
    loc_diff = []
    commits = list(repo.iter_commits())
    progress = tqdm(total=len(commits),
                    desc=f"Fetching {len(commits)} commits")
    for commit in reversed(commits):
        stat = commit.stats.total
        loc_diff.append(
            [
                commit.committed_datetime.isoformat(),
                stat["insertions"] - stat["deletions"],
            ]
        )
        progress.update(1)
    return prepare_commits_dataframe(loc_diff)


def prepare_commits_dataframe(commits):
    commits = pd.DataFrame(commits, columns=["date", "delta"])
    commits.date = pd.to_datetime(commits.date)
    commits.set_index(["date"], inplace=True)
    return commits


def plot_total_lines(
        commits, git_dir, log_scale):
    _delta = commits.delta
    plot_data = _delta.cumsum()

    ylabel = "number of lines"
    if log_scale:
        plot_data = (plot_data + 1).apply(math.log10)
        ylabel = "log number of lines"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_data.index,
                  y=plot_data.values, mode="lines"))
    fig.update_layout(
        title=f"Number of Lines Progress in {os.path.basename(git_dir)}",
        xaxis_title="Date",
        yaxis_title=ylabel,
    )
    fig.update_yaxes(range=[0, 1.1 * plot_data.max()])
    # fig.show()
    fig.write_html(f"{os.path.basename(git_dir)}.html")
    print(f"Saved to {os.path.basename(git_dir)}.html")


if __name__ == "__main__":
    # Usage: main("/path/to/git/repo")
    main("../../lua")
