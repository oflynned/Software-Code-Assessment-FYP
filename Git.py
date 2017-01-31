from Helpers import CommandLine as cl

import json
import re


class GitCL:
    def __init__(self):
        pass

    @staticmethod
    def clone_repo(account, repo):
        cl.execute_cmd_print("git clone http://www.github.com/" + account + "/" + repo)

    @staticmethod
    def get_commit_changes(repo):
        return cl.execute_cmd_get_result("cd " + repo + "; git show --name-only").decode("utf-8")

    @staticmethod
    def set_repo_commit(repo, head):
        cl.execute_cmd_get_result("cd " + repo + "; git reset --hard " + head)

    @staticmethod
    def get_auth_details():
        with open("../auth.json", "r") as f:
            data = json.loads(f.read())
            username = data["username"]
            password = data["password"]
            return username, password

    @staticmethod
    def get_files_changed(repo, head):
        changes = GitCL.get_commit_changes(repo)
        change_details = list(filter(None, re.split("\n", changes)))

        commit_sha = str(change_details[0]).replace("commit", "").strip()
        author = re.sub("[\s+]", " ", str(change_details[1]).replace("Author:", "").strip())
        date = re.sub("[\s+]", " ", str(change_details[2]).replace("Date:", "").strip())

        files = []

        for i, value in enumerate(change_details):
            if i > 3:
                files.append(value)

        print(len(files), "files changed in commit", head)
        return files
