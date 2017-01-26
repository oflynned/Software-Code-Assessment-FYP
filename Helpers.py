import json
import subprocess
import base64
import re
import csv


class JSON:
    @staticmethod
    def pretty_print_json(file):
        print(json.dumps(file, indent=4, sort_keys=True))


class Commit:
    @staticmethod
    def obfuscate_identity(real_identity):
        return base64.b16encode(bytes(real_identity, 'utf-8'))

    @staticmethod
    def deobfuscate_identity(hashed_identity):
        return base64.b16decode(bytes(hashed_identity, 'utf-8'))


class CodeFile:
    @staticmethod
    def get_file(repo_dir, file_dir):
        directory = CommandLine.get_full_dir(repo_dir, file_dir)
        with open(directory, "r") as f:
            return f.read()

    @staticmethod
    def analyse_code(repo):
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc * --total-average").decode(
            "utf-8").split("\n")
        return result[len(result) - 1]

    @staticmethod
    def get_cyclomatic_complexity(repo):
        result = CommandLine.execute_cmd_get_result("cd " + repo + "; radon cc * -a").decode("utf-8").split("\n")
        return result

    @staticmethod
    def get_raw_metrics(repo):
        # TODO parse these results to xml schema or something?
        results = CommandLine.execute_cmd_get_result("cd " + repo + "; radon raw *").decode("utf-8").split("\n")
        metrics = []

        for i, result in enumerate(results):
            # file name
            if i % 12 == 0:
                # file name, loc, lloc, sloc, num comments, single comments, multi, blank
                # TODO comments tuple: c%l, c%s, c+m+l <<< not dealt with rn
                metric = dict()
                metric["file_name"] = results[i].strip()
                metric["loc"] = CodeFile.strip_data(results[i+1])
                metric["lloc"] = CodeFile.strip_data(results[i+2])
                metric["sloc"] = CodeFile.strip_data(results[i+3])
                metric["comments_total_number"] = CodeFile.strip_data(results[i+4])
                metric["comments_single_line"] = CodeFile.strip_data(results[i+5])
                metric["comments_multi_line"] = CodeFile.strip_data(results[i+6])
                metric["comments_blank_line"] = CodeFile.strip_data(results[i+7])

                metrics.append(metric)

        """
        for i, metric in enumerate(metrics):
            print(metric, "\n")
        """

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
    def export_metrics(metrics):
        with open('raw_metrics.csv', 'w') as f:
            for metric in metrics:
                w = csv.DictWriter(f, metric.keys())
                w.writeheader()
                w.writerow(metric)


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
