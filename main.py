#!/usr/bin/env python3
import os

import requests
from requests.auth import HTTPBasicAuth

from Git import GitCL
from Helpers import CodeFile

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

    print("Analysing", str(len(commit_list)), "commits ...")

    """

    for commit in reversed(commit_list):
        # commit[2] = Commit.obfuscate_identity(commit[2])
        print(commit)

    print("Total commits:", len(commit_list))
    oldest_commit = commit_list[1]
    GitCL.set_repo_commit(REPO_NAME, oldest_commit[1])
    author = oldest_commit[2]
    time = oldest_commit[3]
    CodeFile.get_raw_metrics(REPO_NAME)
    """

    newest_commit_head = commit_list[len(commit_list) - 1][1]
    oldest_commit_head = commit_list[0][1]
    GitCL.set_repo_commit(REPO_NAME, oldest_commit_head)
    raw_metrics = []

    # inverted traversal of the commit list (oldest to newest)
    for i, commit in enumerate(reversed(commit_list)):
        author = commit[2]
        time = commit[3]

        GitCL.set_repo_commit(REPO_NAME, commit[1])
        # files = GitCL.get_files_changed(REPO_NAME, commit[1])
        # print(files, "\n")

        # iterate through files changed to get score
        # print(CodeFile.analyse_code(REPO_NAME), author, time)
        print(CodeFile.get_raw_metrics(REPO_NAME))
        raw_metrics.append(CodeFile.get_raw_metrics(REPO_NAME))
        print("Appending metrics for commit", commit[1], str(i))

    print("Exporting metrics for", REPO_NAME, "...")
    CodeFile.export_metrics(raw_metrics)


def main():
    get_repo_data()


if __name__ == "__main__":
    main()
