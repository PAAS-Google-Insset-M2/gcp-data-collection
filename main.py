import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()

api_key = os.environ.get("JCDECAUX_API_KEY")
print(api_key)

contract_name = os.environ.get("JCDECAUX_CONTRACT", "amiens")
print(contract_name)

# The ID of your GCS bucket
bucket_name = os.environ.get("BUCKET_NAME")
print(bucket_name)


# Write to bucket
def write_in_bucket(contents):
    """Uploads a file to the bucket."""
    # Instantiates a client
    storage_client = storage.Client()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destination_blob_name = f"velo-lib-amiens-data_{timestamp}.json"

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(json.dumps(contents), content_type="application/json")
    # blob.upload_from_string(contents)

    print(
        f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}."
    )


def get_data(req, res):
    # Print out the data from Pub/Sub, to prove that it worked
    # print(
    #     "Hello, " + base64.b64decode(cloud_event.data["message"]["data"]).decode() + "!"
    # )

    # Call API here
    api = f"https://api.jcdecaux.com/vls/v1/stations?contract={contract_name}&apiKey={api_key}"
    response = requests.get(f"{api}")

    print("response")
    print(response)

    if response.status_code == 200:
        print("successfully fetched the data")
        write_in_bucket(response.json())
    else:
        print(f"Hello person, there's a {response.status_code} error with your request")
