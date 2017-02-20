from pymongo import *


class Persistence:
    COMMITS_COL = "commits"
    AVG_COMPLEXITY_COL = "average_complexity"
    CYCLOMATIC_COMPLEXITY_COL = "cyclomatic_complexity"
    MAINTAINABILITY_COL = "maintainability"
    RAW_METRICS_COL = "raw_metrics"

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/code_analysis')

    def insert_document(self, new_doc, repo, col):
        db = self.client[repo]
        db[col].insert_one(new_doc)

    def insert_documents(self, new_docs, repo, col):
        db = self.client[repo]
        db[col].insert(new_docs)

    def get_all_data(self, repo, col):
        db = self.client[repo]
        return db[col].find().sort("time")

    def get_constrained_data(self, repo, col, constraint):
        db = self.client[repo]
        return db[col].find(constraint).sort("time")

    def purge_db(self, repo=None, col=None):
        db = self.client

        if col is None:
            db.drop_database(repo)
        else:
            db[repo][col].drop_collection(col)
