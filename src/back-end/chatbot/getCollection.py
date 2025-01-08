import pymongo

class GetCollection:
    def __init__(self,
                mongodbUri: str,
                dbName: str,
                dbCollection: str):
        """
        Initialize the RAG class.
        """
        self.mongo_uri = mongodbUri
        self.dbName = dbName
        self.collection_name = dbCollection
        self.client = None
        self.db = None
        self.collection = None
        self.connect_mongodb()

    def connect_mongodb(self):
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            print("Connection to MongoDB successful")
            return self.client              
        except pymongo.errors.ConnectionFailure as e:
            print(f"Connection failed: {e}")
    def get_collection(self):
        """
        Get the collection from the MongoDB database.

        Args:
        collection_name (str): Name of the collection to retrieve.

        Returns:
        pymongo.collection.Collection: The collection object.
        """
        try:
            self.db = self.client[self.dbName]
            collection = self.db[self.collection_name]
            print(f"Collection '{self.collection_name}' retrieved successfully.")
            return collection
        except pymongo.errors.CollectionInvalid as e:
            print(f"Error retrieving collection: {e}")
            return None
if __name__ == "__test__":
    mongodb_uri = "mongodb+srv://andt:snn5T*6fFP5P5zt@jobs.utyvo.mongodb.net/?retryWrites=true&w=majority&appName=jobs"
    db_name = "product"
    collection_name = "sendo"
    client = GetCollection(mongodb_uri, db_name, collection_name)
    collection=client.get_collection()
    for item in collection.find().limit(1):
        print(item)