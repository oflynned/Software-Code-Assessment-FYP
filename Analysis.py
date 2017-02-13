from Helpers import CommandLine, File

import lizard
import radon
import re


class Sonar:
    def __init__(self):
        pass

    @staticmethod
    def sonar_analysis(repo_dir, version):
        CommandLine.execute_cmd_print(
            "cd " + repo_dir + "; sonar-scanner -Dsonar.sources=. -Dsonar.projectKey=" + repo_dir +
            " -Dsonar.projectVersion=" + str(version))

    @staticmethod
    def purge_repo_analysis(project):
        pass


class Lizard:
    def __init__(self):
        pass

    @staticmethod
    def get_cyclomatic_complexity(repo):
        results = lizard.analyze("./" + repo, None, 2)
        print(results.__dict__)


class Radon:
    def __init__(self):
        pass

    @staticmethod
    def analyse_code(repo):
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc *").decode(
            "utf-8").split("\n")
        return result[len(result) - 1]

    @staticmethod
    def get_cyclomatic_complexity(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc * -s -j").decode("utf-8").split("\n")

        metrics = list()
        metrics.append(File.get_commit_details(commit))
        metrics.append(File.get_json_from_cmd(results))
        metrics[1]["commit_head"] = commit[1]

        return metrics

    @staticmethod
    def get_raw_metrics(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon raw * -j").decode("utf-8").split("\n")
        metrics = list()

        metrics.append(File.get_commit_details(commit))
        metrics.append(File.get_json_from_cmd(results))

        return metrics

    @staticmethod
    def get_maintainability_index(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon mi * -j").decode("utf-8").split("\n")

        metrics = list()
        metrics.append(File.get_commit_details(commit))
        metrics.append(File.get_json_from_cmd(results))

        return metrics

    @staticmethod
    def get_average_complexity(repo, commit):
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc * --total-average").decode(
            "utf-8").split("\n")
        complexity = results[len(results) - 1]
        complexity = re.search("\d+\.?\d*", complexity).group(0)

        metrics = list()
        metrics.append({"commit_head": commit[1]})
        metrics[0]["avg_complexity"] = complexity

        return metrics
