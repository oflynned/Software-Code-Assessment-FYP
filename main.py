#!/usr/bin/env python3
import os

import requests
from requests.auth import HTTPBasicAuth

from Git import GitCL
from Analysis import Radon
from Graph import Neo
from Helpers import File
import json, re

import lizard
from Persistence import Persistence

# samshadwell/TrumpScript
# oflynned/AI-Art
# joke2k/faker
# Russell91/pythonpy
# ajalt/fuckitpy

REPO_ACCOUNT = "oflynned"
REPO_NAME = "AI-Art"
PAGINATION = 100

repos = [
    ["oflynned", "AI-Art"],
    ["samshadwell", "TrumpScript"],
    ["joke2k", "faker"],
    ["Russell91", "pythonpy"],
    ["ajalt", "fuckitpy"]
]


def iterate_over_commits(commit_list):
    print("Analysing", str(len(commit_list)), "commits", "...")

    # debug drop all tables to clean table constantly
    persistence = Persistence()
    persistence.purge_db(REPO_NAME)

    # set oldest commit first
    GitCL.set_repo_commit(REPO_NAME, commit_list[0][1])

    total_commits = []

    # inverted traversal of the commit list (oldest to newest)
    for i, commit in enumerate(commit_list):
        head = commit[1]
        author = commit[2]
        time = commit[3]
        version = str(i + 1)

        # --hard reset to sha head
        print("Commit " + version, head, author, time)
        GitCL.set_repo_commit(REPO_NAME, head)

        # iterate through files changed to get score
        print("Appending metrics for commit", head)

        generate_radon_stats(commit, persistence)
        total_commits.append(commit)

        # Neo.generate_graph(total_commits)


# generate metrics per file changed per commit
def generate_file_stats(head, i):
    files_changes = GitCL.get_files_changed(REPO_NAME, head)
    for file in files_changes:
        metrics = lizard.analyze_file(REPO_NAME + "/" + file)
        functions = []
        for function in metrics.function_list:
            this_function = function.__dict__
            this_file = os.path.splitext(os.path.basename(file))[0]
            functions.append(this_function)
            File.export_metrics(REPO_NAME, this_file, functions, i, True)


# generate metrics per commit via radon halstead analysis
def generate_radon_stats(commit, persistence):
    cyclomatic_metrics = Radon.get_cyclomatic_complexity(REPO_NAME, commit)
    average_complexity = Radon.get_average_complexity(REPO_NAME, commit)
    maintainability_metrics = Radon.get_maintainability_index(REPO_NAME, commit)

    commit_head = commit[1]
    maintainability_metrics[1]["commit"] = commit_head

    print("Exporting metrics for", REPO_NAME, "to DB ...")

    maintainability_items = list()
    maintainability_items.append({"commit": commit_head})

    maintainability_keys = dict()
    for file in maintainability_metrics[1]:
        maintainability_keys[os.path.splitext(file)[0]] = maintainability_metrics[1][file]

    maintainability_items[0]["files"] = [maintainability_keys]

    # insert meta data about commits
    persistence.insert_document(cyclomatic_metrics[0], REPO_NAME, Persistence.COMMITS_COL)
    persistence.insert_document(average_complexity[0], REPO_NAME, Persistence.AVG_COMPLEXITY_COL)
    persistence.insert_document(maintainability_items[0], REPO_NAME, Persistence.MAINTAINABILITY_COL)

    # this loop complexity is ironic for something to get the complexity over files ...
    # gets the metrics for complexities over functions per file per commit
    for metric in cyclomatic_metrics:
        for file in metric:
            curr_file = metric[file]
            if type(curr_file) == list:
                for item in curr_file:
                    item["commit"] = commit_head
                    persistence.insert_document(item, REPO_NAME, Persistence.CYCLOMATIC_COMPLEXITY_COL)

    # for complexity in persistence.get_all_data(REPO_NAME, Persistence.CYCLOMATIC_COMPLEXITY_COL):
    #     print(complexity)

    #for avg in persistence.get_all_data(REPO_NAME, Persistence.AVG_COMPLEXITY_COL):
    #    print(avg)

    for maintainability in persistence.get_all_data(REPO_NAME, Persistence.MAINTAINABILITY_COL):
        print(maintainability)

    #for commit in persistence.get_all_data(REPO_NAME, Persistence.COMMITS_COL):
    #    print(commit)


def get_repo_data(commit_list):
    username, password = GitCL.get_auth_details()

    i = 1
    curr_commit_count = -1

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


def main():
    commit_list = []
    get_repo_data(commit_list)
    iterate_over_commits(commit_list)


if __name__ == "__main__":
    main()
