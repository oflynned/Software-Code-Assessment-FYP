#!/usr/bin/env python3
import os

import requests
from requests.auth import HTTPBasicAuth

from Git import GitCL
from Helpers import CodeFile

import json

# samshadwell/TrumpScript
# oflynned/AI-Art

REPO_ACCOUNT = "samshadwell"
REPO_NAME = "TrumpScript"
PAGINATION = 100


def get_repo_data():
    username, password = GitCL.get_auth_details()

    i = 1
    curr_commit_count = -1
    commit_list = []

    print("Getting commits for", REPO_ACCOUNT, "/", REPO_NAME, "...")

    while curr_commit_count != 0:
        req = requests.get(
            "http://api.github.com/repos/" + REPO_ACCOUNT + "/" + REPO_NAME +
            "/commits?per_page=" + str(PAGINATION) + "&page=" + str(i),
            auth=HTTPBasicAuth(username, password))

        json_full_history = req.json()
        curr_commit_count = len(json_full_history)

        for j, item in enumerate(json_full_history):
            if item["author"] is not None:
                commit_list.append(
                    [item["sha"], item["sha"][0:7], item["commit"]["author"]["email"],
                     item["commit"]["author"]["date"]])

            if not os.path.isdir(REPO_NAME):
                GitCL.clone_repo(REPO_ACCOUNT, REPO_NAME)

        i += 1

    print("Analysing", str(len(commit_list)), "commits", "...")

    newest_commit_head = commit_list[len(commit_list) - 1][1]
    oldest_commit_head = commit_list[0][1]
    GitCL.set_repo_commit(REPO_NAME, oldest_commit_head)

    raw_metrics = []
    average_complexity = []
    cyclomatic_metrics = []
    maintainability_metrics = []

    # limit list to first 25
    commit_list = list(reversed(commit_list))
    # commit_list = commit_list[:25]

    # inverted traversal of the commit list (oldest to newest)
    for i, commit in enumerate(commit_list):
        head = commit[1]
        author = commit[2]
        time = commit[3]
        version = str(i + 1)

        print("Commit " + version, head, author, time)
        GitCL.set_repo_commit(REPO_NAME, head)

        # iterate through files changed to get score
        print("Appending metrics for commit", commit[1], str(i))
        raw_metrics.append(CodeFile.get_raw_metrics(REPO_NAME, commit))
        cyclomatic_metrics.append(CodeFile.get_cyclomatic_complexity(REPO_NAME, commit))
        maintainability_metrics.append(CodeFile.get_maintainability_index(REPO_NAME, commit))
        average_complexity.append(CodeFile.get_average_complexity(REPO_NAME, commit))

        # perhaps move to end of function?
        print("Exporting metrics for", REPO_NAME, "...")
        CodeFile.export_metrics(REPO_NAME, "raw", raw_metrics)
        CodeFile.export_metrics(REPO_NAME, "cyclomatic", cyclomatic_metrics)
        CodeFile.export_metrics(REPO_NAME, "maintainability", maintainability_metrics)
        CodeFile.export_metrics(REPO_NAME, "average_complexity", average_complexity)


def main():
    get_repo_data()


if __name__ == "__main__":
    main()
