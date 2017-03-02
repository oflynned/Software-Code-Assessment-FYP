#!/usr/bin/env python3
import os

import lizard
import requests
from requests.auth import HTTPBasicAuth

from Analysis import Radon
from Git import GitCL
from Helpers import File
from Helpers import JSON
from Persistence import Persistence
from fnmatch import fnmatch

PAGINATION = 100

repos_self_curated = [
    ["oflynned", "AI-Art"],
    ["samshadwell", "TrumpScript"],
    ["joke2k", "faker"],
    ["Russell91", "pythonpy"],
    ["ajalt", "fuckitpy"],
    ["nvbn", "thefuck"],
    ["binux", "pyspider"],
    ["scikit-learn", "scikit-learn"],
    ["pyca", "cryptography"],
    ["pyca", "pyopenssl"]
]

repos = [
    repos_self_curated[9]
]


# TODO harvest n, perform analysis, clear, harvest n more from that point, ...
# TODO prevents harvesting >1,000,000 repos in one go and analysing in one block
def harvest_repositories(username, password):
    i = 1
    curr_repo_count = -1
    curated_repos = []

    url = "https://api.github.com/search/repositories?q=language:python&order=desc&page=" + str(i)
    req = requests.get(url, auth=HTTPBasicAuth(username, password)).json()
    repo_count = req["total_count"]

    # debug sentinel cap of n pages of repositories
    # while curr_repo_count != 0:
    while i < 2:
        url = "https://api.github.com/search/repositories?q=language:python&order=desc" + \
              "&page=" + str(i) + "&per_page=" + str(PAGINATION)
        req = requests.get(url, auth=HTTPBasicAuth(username, password))

        repo_curation = req.json()
        curr_repo_count = len(repo_curation)

        print("Retrieved commit pagination", "(" + str(PAGINATION * i) + ")", "...")

        for j, item in enumerate(repo_curation["items"]):
            curated_repos.append([item["owner"]["login"], item["name"]])

        i += 1

    return repo_count, curated_repos


def iterate_over_commits(repo_name, commit_list):
    # invert list to iterate from start to end
    commit_list = list(reversed(commit_list))
    print("Analysing", str(len(commit_list)), "commits", "...")

    # drop already existing tables to scrub properly
    persistence = Persistence()
    persistence.purge_db(repo_name)

    # set oldest commit first
    GitCL.set_repo_commit(repo_name, commit_list[0][1])
    total_commits = []

    # inverted traversal of the commit list (oldest to newest)
    for i, commit in enumerate(commit_list):
        head = commit[1]
        author = commit[2]
        time = commit[3]
        version = str(i + 1)

        # --hard reset to sha head
        print("\nCommit " + version, head, author, time)
        GitCL.set_repo_commit(repo_name, head)

        # iterate through files changed to get score
        print("Appending metrics for commit", head)

        generate_radon_stats(repo_name, commit, persistence)
        total_commits.append(commit)


# generate metrics per file changed per commit
# TODO does not use MongoDB collection
def generate_file_stats(repo_name, head, i):
    files_changes = GitCL.get_files_changed(repo_name, head)
    for file in files_changes:
        metrics = lizard.analyze_file(repo_name + "/" + file)
        functions = []
        for function in metrics.function_list:
            this_function = function.__dict__
            this_file = os.path.splitext(os.path.basename(file))[0]
            functions.append(this_function)
            File.export_metrics(repo_name, this_file, functions, i, True)


# generate metrics per commit via radon halstead analysis
def generate_radon_stats(repo_name, commit, persistence):
    print("Exporting metrics for", repo_name, "to DB ...")

    determine_commit_details(repo_name, commit, persistence)
    determine_average_complexity(repo_name, commit, persistence)
    determine_cyclomatic_complexity(repo_name, commit, persistence)
    determine_maintainability(repo_name, commit, persistence)
    determine_raw_metrics(repo_name, commit, persistence)


def determine_commit_details(repo_name, commit, persistence):
    persistence.insert_document(File.get_commit_details(commit), repo_name, Persistence.COMMITS_COL)


def determine_average_complexity(repo_name, commit, persistence):
    average_complexity = Radon.get_average_complexity(repo_name, commit)
    persistence.insert_document(average_complexity[0], repo_name, Persistence.AVG_COMPLEXITY_COL)


def determine_cyclomatic_complexity(repo_name, commit, persistence):
    cyclomatic_metrics = Radon.get_cyclomatic_complexity(repo_name, commit)

    # gets the metrics for complexities over functions per file per commit
    for metric in cyclomatic_metrics:
        for file in metric:
            curr_file = metric[file]
            if type(curr_file) == list:
                for item in curr_file:
                    item["commit"] = commit[1]
                    persistence.insert_document(item, repo_name, Persistence.CYCLOMATIC_COMPLEXITY_COL)


def determine_raw_metrics(repo_name, commit, persistence):
    raw_metrics = Radon.get_raw_metrics(repo_name, commit[1])

    del raw_metrics[0]

    raw_insert = dict()
    raw_items = list()

    for file in raw_metrics[0]:
        if os.path.splitext(file)[1] == ".py":
            metric = raw_metrics[0][file]
            metric["file"] = repo_name + "/" + file
            raw_items.append(metric)

    raw_insert["files"] = raw_items
    raw_insert["commit"] = commit[1]

    persistence.insert_document(raw_insert, repo_name, Persistence.RAW_METRICS_COL)


def determine_maintainability(repo_name, commit, persistence):
    # iterate over all files rather than one huge chunk
    for path, subdirs, files in os.walk(repo_name):
        for name in files:
            file_path = os.path.join(path, name)
            if fnmatch(name, "*.py"):
                maintainability_metrics = Radon.get_file_maintainability_index(file_path)

                # remove the .py extension
                maintainability_metrics[0] = {os.path.splitext(file_path)[0]: maintainability_metrics[0][file_path]}
                maintainability_metrics[0]["commit"] = commit[1]

                JSON.pretty_print_json(maintainability_metrics[0])
                persistence.insert_document(maintainability_metrics[0], repo_name, Persistence.MAINTAINABILITY_COL)


def print_collection(repo_name, persistence, collection):
    for complexity in persistence.get_all_data(repo_name, collection):
        print(complexity)


def get_repo_data(repo_name, repo_account, commit_list):
    username, password = GitCL.get_auth_details()

    i = 1
    curr_commit_count = -1

    print("Getting commits for", repo_account, "/", repo_name, "...")

    while curr_commit_count != 0:
        url = "http://api.github.com/repos/" + repo_account + "/" + repo_name + \
              "/commits?per_page=" + str(PAGINATION) + "&page=" + str(i)
        req = requests.get(url, auth=HTTPBasicAuth(username, password))

        json_full_history = req.json()
        curr_commit_count = len(json_full_history)

        print("Retrieved commit pagination", "(" + str(PAGINATION * i) + ")", "...")

        for j, item in enumerate(json_full_history):
            if item["author"] is not None:
                commit_list.append(
                    [item["sha"],
                     item["sha"][0:7],
                     item["commit"]["author"]["email"],
                     item["commit"]["author"]["date"]])

            if not os.path.isdir(repo_name):
                GitCL.clone_repo(repo_account, repo_name)

        i += 1


def main():
    username, password = GitCL.get_auth_details()

    # mass harvesting, uncomment to curate all python repos on GitHub
    # repos is a list of curated [repo_name, repo_account] of length ~1,511,164
    # must change to harvest a pagination, process, store, continue with second pagination ...
    # repo_count, repos_curated = harvest_repositories(username, password)

    for repo in repos:
        commit_list = []
        repo_account, repo_name = repo[0], repo[1]
        get_repo_data(repo_name, repo_account, commit_list)
        iterate_over_commits(repo_name, commit_list)


if __name__ == "__main__":
    main()
