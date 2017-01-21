import subprocess
import json
import re


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
    def analyse_code(repo, file):
        dir = CommandLine.get_full_dir(repo, file)
        CommandLine.execute_cmd_get_result("idea metrics")


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
