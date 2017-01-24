#!/usr/bin/env python3
import os

import requests
from requests.auth import HTTPBasicAuth

from Git import GitCL
from Helpers import CodeFile

# samshadwell/TrumpScript
REPO_ACCOUNT = "samshadwell"
REPO_NAME = "TrumpScript"


def get_repo_data():
    username, password = GitCL.get_auth_details()
    head_list = []

    i = 1
    curr_commit_count = -1
    # to limit over sampling as I only have 5000 requests
    max_commit_limit = 100

    print("Getting commits for", REPO_ACCOUNT, "/", REPO_NAME, "...")

    while curr_commit_count != 0:
        req = requests.get(
            "http://api.github.com/repos/" + REPO_ACCOUNT + "/" + REPO_NAME + "/commits?per_page=100&page=" + str(i),
            auth=HTTPBasicAuth(username, password))
        i += 1

        json_full_history = req.json()
        curr_commit_count = len(json_full_history)

        sha_commit_list = []
        for item in json_full_history:
            sha_commit_list.append(item["sha"])

        # commit head is first 7 chars
        for sha in sha_commit_list:
            head_list.append(sha[0:7])

        if not os.path.isdir(REPO_NAME):
            GitCL.clone_repo(REPO_ACCOUNT, REPO_NAME)

    print("Total commits:", len(head_list))

    newest_commit = head_list[len(head_list) - 1]
    oldest_commit = head_list[0]

    GitCL.set_repo_commit(REPO_NAME, oldest_commit)

    # inverted traversal of the commit list (oldest to newest)
    for head in reversed(head_list):
        GitCL.set_repo_commit(REPO_NAME, head)
        files = GitCL.get_files_changed(REPO_NAME, head)

        # print(files, "\n")

        # iterate through files changed to get score
        print(CodeFile.analyse_code(REPO_NAME))


def main():
    get_repo_data()


if __name__ == "__main__":
    main()
