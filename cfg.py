import os

config = {
    'mongo_uri': f'mongodb://{os.environ.get("MONGO_USER")}:{os.environ.get("MONGO_PASSWORD")}@cluster0-shard-00-00.pcszv.mongodb.net:27017,cluster0-shard-00-01.pcszv.mongodb.net:27017,cluster0-shard-00-02.pcszv.mongodb.net:27017/{os.environ.get("MONGO_DB")}?ssl=true&replicaSet=atlas-duk28h-shard-0&authSource=admin&retryWrites=true&w=majority'
}