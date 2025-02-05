import pandas as pd
import pymongo
import json
class CSVToMongoDB:
    def __init__(self, mongodb_uri: str, db_name: str, collection_name: str):
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def ingest_csv(self, csv_file_path: str):
        """
        Ingest a CSV file into the MongoDB collection.

        Args:
        csv_file_path (str): The path to the CSV file.
        """
        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(csv_file_path)

            # Convert DataFrame to a list of dictionaries
            data = df.to_dict(orient='records')

            # Insert data into MongoDB collection
            self.collection.insert_many(data)
            print(f"Successfully ingested {len(data)} records into MongoDB.")
        except Exception as e:
            print(f"Error ingesting CSV to MongoDB: {e}")

    def ingest_json(self, json_file_path: str):
        """
        Ingest a JSON file into the MongoDB collection.

        Args:
        json_file_path (str): The path to the JSON file.
        """
        try:
            # Load JSON data from a file
            with open(json_file_path, 'r') as file:
                json_data = json.load(file)

            # Insert JSON data into MongoDB collection
            if isinstance(json_data, list):
                # If the JSON data is a list of dictionaries, use insert_many
                self.collection.insert_many(json_data)
            else:
                # If the JSON data is a single dictionary, use insert_one
                self.collection.insert_one(json_data)

            print(f"Successfully ingested JSON data into MongoDB.")
        except Exception as e:
            print(f"Error ingesting JSON to MongoDB: {e}")

# Example usage
if __name__ == "__main__":
    # Load environment variables from .env file
    import dotenv
    env = dotenv.dotenv_values(".env")
    mongodb_uri= env.get("MONGODB_URI")
    db_name = "product"
    collection_name = "sendo"
    # csv_file_path = "lastoflast.csv"
    # json_file_path = "data.json"

    # Create an instance of the CSVToMongoDB class
    ingestor = CSVToMongoDB(mongodb_uri, db_name, collection_name)

    # Ingest CSV data
    #ingestor.ingest_csv(csv_file_path)
    json_file_path=''
    # Ingest JSON data
    ingestor.ingest_json(json_file_path)