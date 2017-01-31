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

    """
    BELOW IS FOR RADON
    """

    @staticmethod
    def analyse_code(repo):
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc *").decode(
            "utf-8").split("\n")
        return result[len(result) - 1]

    @staticmethod
    def get_cyclomatic_complexity(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc * -s -j").decode("utf-8").split("\n")
        metrics = []

        detail = dict()
        detail["sha"] = commit[0]
        detail["head"] = commit[1]
        detail["author"] = commit[2]
        detail["time"] = commit[3]

        metrics.append(detail)
        results = json.loads(str(results[0]))
        metrics.append(results)

        return metrics

    @staticmethod
    def get_raw_metrics(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon raw *").decode("utf-8").split("\n")
        metrics = []

        detail = dict()
        detail["sha"] = commit[0]
        detail["head"] = commit[1]
        detail["author"] = commit[2]
        detail["time"] = commit[3]
        metrics.append(detail)

        for i, result in enumerate(results):
            # file name
            if i % 12 == 0:
                # file name, loc, lloc, sloc, num comments, single comments, multi, blank
                metric = dict()
                metric["file_name"] = results[i].strip()
                metric["loc"] = CodeFile.strip_data(results[i + 1])
                metric["lloc"] = CodeFile.strip_data(results[i + 2])
                metric["sloc"] = CodeFile.strip_data(results[i + 3])
                metric["comments_total_number"] = CodeFile.strip_data(results[i + 4])
                metric["comments_single_line"] = CodeFile.strip_data(results[i + 5])
                metric["comments_multi_line"] = CodeFile.strip_data(results[i + 6])
                metric["comments_blank_line"] = CodeFile.strip_data(results[i + 7])

                metrics.append(metric)

        for i, metric in enumerate(metrics):
            print(metric, "\n")

        return metrics

    @staticmethod
    def strip_data(item):
        return re.sub("[^0-9]", "", str(item).strip())

    @staticmethod
    def get_halstead_metrics(repo):
        pass

    @staticmethod
    def get_maintainability_index(repo):
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon mi *").decode("utf-8")
        return result

    @staticmethod
    def export_metrics(repo, metrics):
        with open(repo + '_raw_metrics.json', 'w') as f:
            f.write(JSON.pretty_print_json(metrics))


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
