import json
import subprocess
import base64
import re
import os


class JSON:
    def __init__(self):
        pass

    @staticmethod
    def pretty_print_json(raw_file):
        return json.dumps(raw_file, indent=4, sort_keys=True)


class Commit:
    def __init__(self):
        pass

    @staticmethod
    def obfuscate_identity(real_identity):
        encoding = base64.encodebytes(bytes(real_identity, 'utf8'))
        encoding = encoding.decode("utf-8").replace("\n", "")
        return encoding

    @staticmethod
    def deobfuscate_identity(hashed_identity):
        decoded = base64.decodebytes(bytes(hashed_identity, 'utf-8'))
        decoded = decoded.decode("utf-8")
        return decoded


class File:
    def __init__(self):
        pass

    @staticmethod
    def get_file(repo_dir, file_dir):
        directory = CommandLine.get_full_dir(repo_dir, file_dir)
        with open(directory, "r") as f:
            return f.read()

    @staticmethod
    def strip_data(item):
        return re.sub("[^0-9]", "", str(item).strip())

    @staticmethod
    def export_metrics(repo, metric_type, metrics, commit, is_function=False):
        if not os.path.exists("Metrics"):
            os.makedirs("Metrics")

        if not os.path.exists("Metrics/" + repo):
            os.makedirs("Metrics/" + repo)

        if not os.path.exists("Metrics/" + repo + "/Files/"):
            os.makedirs("Metrics/" + repo + "/Files/")

        if is_function is True:
            with open("Metrics/" + repo + "/Files/" + metric_type + "_" + str(commit) + '.json', 'w') as f:
                f.write(JSON.pretty_print_json(metrics))
        else:
            with open("Metrics/" + repo + "/" + metric_type + "_" + str(commit) + '.json', 'w') as f:
                f.write(JSON.pretty_print_json(metrics))

    @staticmethod
    def get_json_from_cmd(cmd_output):
        return json.loads(str(cmd_output[0]))

    @staticmethod
    def get_commit_details(repo_name, commit, iteration, max_iterations):
        detail = dict()
        detail["sha"] = commit[0]
        detail["head"] = commit[1]
        detail["author"] = commit[2]
        detail["time"] = commit[3]
        detail["iteration"] = iteration
        detail["max_iterations"] = max_iterations
        detail["repo"] = repo_name

        return detail


class CommandLine:
    def __init__(self):
        pass

    @staticmethod
    def get_full_dir(repo_dir, file_dir):
        return repo_dir + "/" + file_dir

    @staticmethod
    def execute_cmd_print(command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        print(process.communicate()[0].strip())

    @staticmethod
    def execute_cmd_get_result(command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        return process.communicate()[0].strip()
