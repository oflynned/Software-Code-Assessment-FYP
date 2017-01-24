import json
import subprocess


class JSON:
    @staticmethod
    def pretty_print_json(file):
        print(json.dumps(file, indent=4, sort_keys=True))


class Commit:
    @staticmethod
    def get_sha():
        pass


class CodeFile:
    @staticmethod
    def get_file(repo_dir, file_dir):
        directory = CommandLine.get_full_dir(repo_dir, file_dir)
        with open(directory, "r") as f:
            return f.read()

    @staticmethod
    def analyse_code(repo):
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc * --total-average").decode("utf-8").split("\n")
        return result[len(result) - 1]

    @staticmethod
    def get_cyclomatic_complexity(repo):
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc * -a").decode("utf-8").split("\n")
        return result

    @staticmethod
    def get_raw_metrics(repo):
        # TODO parse these results to xml schema or something?
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon raw *").decode("utf-8")
        pass

    @staticmethod
    def get_halstead_metrics(repo):
        pass

    @staticmethod
    def get_maintainability_index(repo):
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon mi *").decode("utf-8")
        return result

    @staticmethod
    def export_metrics(data):
        pass


class CommandLine:
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
