import os

config = {
    'mongo_uri': f'mongodb+srv://{os.environ.get("MONGO_USER")}:{os.environ.get("MONGO_PASSWORD")}@{os.environ.get("MONGO_CLUSTER")}.pcszv.mongodb.net/{os.environ.get("MONGO_DB")}?retryWrites=true&w=majority'
}