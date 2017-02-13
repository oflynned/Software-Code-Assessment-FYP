from neo4jrestclient.client import GraphDatabase
import json


class Neo:
    @staticmethod
    def get_auth_details():
        with open("../neo4j_auth.json", "r") as f:
            data = json.loads(f.read())
            username = data["username"]
            password = data["password"]
            return username, password

    @staticmethod
    def login():
        username, password = Neo.get_auth_details()
        host = "http://localhost:7474"

        return GraphDatabase(host, username=username, password=password)

    @staticmethod
    def exists(db, node=None, property=None, value=None):
        filter_node = (":" + node) if node is not None else ''
        filter_value = ("{" + property + ": '" + value + "'}") if property is not None and value is not None else ''
        return db.cypher_query("MATCH(n" + filter_node + filter_value + ")" +
                               " return count(n) > 0 as exists;")[0][0][0]

    @staticmethod
    def generate_file_user_graph(commit, files):
        db = Neo.login()

        """
        user_label = db.labels.create("User")
        file_label = db.labels.create("File")
        user_node = db.nodes.create(name=commit[2])
        """

        for file in files:
            print(file)
            # file_node = db.nodes.create(name=file[])

    @staticmethod
    def generate_graph(commits):
        db = Neo.login()
        user_label = db.labels.create("User")
        commit_label = db.labels.create("Commit")

        for commit in commits:
            # email
            user_node = db.nodes.create(name=commit[2])
            user_label.add(user_node)

            # commit
            commit_node = db.nodes.create(head=commit[1])
            commit_label.add(commit_node)

            user_node.relationships.create("Commits", commit_node, time=commit[3])
