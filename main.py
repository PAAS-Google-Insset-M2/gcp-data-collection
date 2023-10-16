import base64
import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from google.cloud import storage

from cloudevents.http import CloudEvent
import functions_framework

load_dotenv()

api_key = os.environ.get("JCDECAUX_API_KEY")

contract_name = os.environ.get("JCDECAUX_CONTRACT", "amiens")

# The ID of your GCS bucket
bucket_name = os.environ.get("BUCKET_NAME")

# Default, timeout = 5 seconds
timeout = int(os.environ.get("TIMEOUT", "5"))


def write_in_bucket(contents):
    """ Uploads the json data to the bucket. """
    # Instantiates a client
    storage_client = storage.Client()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destination_blob_name = f"velo-data_{timestamp}.json"

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    if contents is None:
        blob.upload_from_string(None)
    else:
        blob.upload_from_string(json.dumps(contents), content_type="application/json")

    print(
        f"{destination_blob_name} with contents uploaded to {bucket_name}."
    )


@functions_framework.cloud_event
def get_data(cloud_event: CloudEvent):
    """
    Retrieves the data for the velo lib bucket. <br>
    Triggered by a new message send to the pub/sub "velo-lib-amiens-topic"
    """
    # Print out the data from Pub/Sub, to prove that it worked
    print(
        "Hello, " + base64.b64decode(cloud_event.data["message"]["data"]).decode() + "!"
    )

    try:
        # Call API here
        payload = {'contract': contract_name, 'apiKey': api_key}
        api = "https://api.jcdecaux.com/vls/v1/stations"
        response = requests.get(f"{api}", params=payload, timeout=timeout)

        if response.status_code == 200:
            print("Successfully fetched the data")
            write_in_bucket(response.json())
        else:
            print(f"Hello person, there's a {response.status_code} error with your request")
            write_in_bucket(None)
    except requests.exceptions.Timeout:
        print('The request TIMED OUT')
        write_in_bucket(None)
    except requests.exceptions.HTTPError:
        print("The attempt to retrieve the data was UNSUCCESSFUL!")
        write_in_bucket(None)
    except requests.exceptions.RequestException as e:
        print("A RequestException occurred:", e)
        write_in_bucket(None)
    except Exception as e:
        print("An error occurred:", e)
        write_in_bucket(None)
