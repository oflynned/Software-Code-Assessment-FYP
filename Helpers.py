import json
import subprocess
import base64
import re


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
        return base64.b16encode(bytes(real_identity))

    @staticmethod
    def deobfuscate_identity(hashed_identity):
        return base64.b16decode(bytes(hashed_identity))


class CodeFile:
    def __init__(self):
        pass

    @staticmethod
    def get_file(repo_dir, file_dir):
        directory = CommandLine.get_full_dir(repo_dir, file_dir)
        with open(directory, "r") as f:
            return f.read()

    # project version is the commit sequence (ie version 3 if at 3rd commit)
    @staticmethod
    def sonar_analysis(repo_dir, version):
        CommandLine.execute_cmd_print(
            "cd " + repo_dir + "; sonar-scanner -Dsonar.sources=. -Dsonar.projectKey=" + repo_dir +
            " -Dsonar.projectVersion=" + str(version))

    @staticmethod
    def purge_repo_analysis(project):
        pass

    # Radon is currently used as the metrics factory
    @staticmethod
    def analyse_code(repo):
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc *").decode(
            "utf-8").split("\n")
        return result[len(result) - 1]

    @staticmethod
    def strip_data(item):
        return re.sub("[^0-9]", "", str(item).strip())

    @staticmethod
    def export_metrics(repo, metric_type, metrics):
        with open(repo + '_' + metric_type + '_metrics' + '.json', 'w') as f:
            f.write(JSON.pretty_print_json(metrics))

    @staticmethod
    def get_json_from_cmd(cmd_output):
        return json.loads(str(cmd_output[0]))

    @staticmethod
    def get_commit_details(commit):
        detail = dict()
        detail["sha"] = commit[0]
        detail["head"] = commit[1]
        detail["author"] = commit[2]
        detail["time"] = commit[3]
        return detail

    @staticmethod
    def get_cyclomatic_complexity(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc * -s -j").decode("utf-8").split("\n")
        metrics = list()

        metrics.append(CodeFile.get_commit_details(commit))
        metrics.append(CodeFile.get_json_from_cmd(results))

        return metrics

    @staticmethod
    def get_raw_metrics(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon raw * -j").decode("utf-8").split("\n")
        metrics = list()

        metrics.append(CodeFile.get_commit_details(commit))
        metrics.append(CodeFile.get_json_from_cmd(results))

        return metrics

    @staticmethod
    def get_maintainability_index(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon mi * -j").decode("utf-8").split("\n")
        metrics = list()

        metrics.append(CodeFile.get_commit_details(commit))
        metrics.append(CodeFile.get_json_from_cmd(results))

        return metrics

    @staticmethod
    def get_average_complexity(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc * --total-average -j").decode("utf-8").split("\n")
        metrics = list()

        metrics.append(CodeFile.get_commit_details(commit))
        metrics.append(CodeFile.get_json_from_cmd(results))

        return metrics


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
