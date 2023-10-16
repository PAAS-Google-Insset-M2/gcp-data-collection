# Gcp-data-collection

#### <u>Student</u> : ZOUNON Ahouefa Sharonn

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#project-description">Project Description</a></li>
    <li><a href="#authentication-on-gcloud">Authentication on gcloud</a></li>
    <li><a href="#cloud-storage-bucket">Cloud Storage (Bucket)</a></li>
    <li><a href="#cloud-pub-sub">CLoud Pub/Sub</a></li>
    <li><a href="#cloud-function">Cloud Function</a></li>
    <li><a href="#cloud-scheduler">Cloud Scheduler</a></li>
    <li><a href="#deploy-the-project">Run the project</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- PROJECT -->

## Project Description

... <br/>
I am using python as programming language.

We are using the [JCDecaux API](https://developer.jcdecaux.com/#/opendata/vls?page=getstarted).

For calling their API, you have to use the following request with the corresponding information:
> GET https://api.jcdecaux.com/vls/v1/stations?contract={contract_name}&apiKey={api_key}

## Authentication on gcloud

For the local development, I had to setup user's credentials. <br />
* Install and initialize the gcloud cli
    ```shell 
      # I am on fedora workstation 38
      sudo dnf install google-cloud-cli  # install
  
      gcloud init  # initialize
  
      gcloud config set project paas-gcp-insset-2023  # change the project
    ```
* Create credential file
    ```shell 
      gcloud auth application-default login
    ```

## Needed APIs

* Cloud Resource Manager [cloudresourcemanager.googleapis.com]
* Pub/Sub API

## Cloud Storage (Bucket)

We can specify the project, the location and the storage class.

My bucket name is: ***velo-lib-amiens*** <br/>
I chose the location: ***EUROPE-WEST9*** (located in Paris) which is the closest to where JCDecaux stores their data. Plus, it has low carbon emission and is also cheap (?). <br/>
I chose the ***standard*** storage class. I thought it would be the best because, I am going to use it after for training the model.

The command line to create a bucket is the following.
```shell 
# I have a configuration file with my default project so I use it to fill the project variable. 
# If you have multiple projects, you have to specify the project ID
# gcloud storage buckets create gs://<bucket_name> --project=<project_id> --default-storage-class=<storage_class> --location=<location> --uniform-bucket-level-access

gcloud storage buckets create gs://velo-lib-amiens --project=$(gcloud config get-value core/project) --default-storage-class=STANDARD --location=europe-west9 --uniform-bucket-level-access
```

## CLoud Pub/Sub

```shell
# Enable the Pub/Sub API
gcloud services enable pubsub.googleapis.com

# Create topic with the desired id (a string)
# gcloud pubsub topics create <id_topic>
gcloud pubsub topics create velo-lib-amiens-topic

# Create a subscription with the desired id and attach it to the created topic using its id
# gcloud pubsub subscriptions create <subscription_name> --topic=<created_topic_id>
gcloud pubsub subscriptions create velo-lib-amiens-sub --topic=velo-lib-amiens-topic

# Receive messages from the subcription
# gcloud pubsub subscriptions pull <sub_id> --auto-ack
```

## Cloud Function

```shell
# APIs
gcloud services enable cloudfunctions.googleapis.com run.googleapis.com cloudbuild.googleapis.com eventarc.googleapis.com

# Deploying the function
gcloud functions deploy python-get-velo-lib-data-function \
--gen2 \
--runtime=python311 \
--region=europe-west9 \
--source=. \
--memory 128Mi \
--entry-point=get_data \
--trigger-topic=velo-lib-amiens-topic \
--env-vars-file=.env.yaml \
--retry

# gcloud functions deploy python-get-velo-lib-data-function --gen2 --runtime=python311 --region=europe-west9 --source=. --entry-point=get_data --trigger-topic=velo-lib-amiens-topic --env-vars-file=.env.yaml --retry

# Triggering the function
gcloud pubsub topics publish velo-lib-amiens-topic --message="Friend"

# See results
gcloud functions logs read \
  --gen2 \
  --region=europe-west9 \
  --limit=5 \
  FUNCTION_NAME  # python-get-velo-lib-data-function


# Delete function
gcloud functions delete python-get-velo-lib-data-function --gen2 --region europe-west9
```

## Cloud Scheduler

```shell
# Enable APIs
gcloud services enable cloudscheduler.googleapis.com pubsub.googleapis.com
```

### Deploy the project
<!-- Add total cost / month -->

#### To stop the running function

### Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com <br />
Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)

<!-- ACKNOWLEDGMENTS -->
### Acknowledgments

Helpful resources!

* [Create bucket on GCP](https://cloud.google.com/storage/docs/creating-buckets#create_a_new_bucket)
* [Deploy function](https://cloud.google.com/functions/docs/create-deploy-gcloud)
* [JCDecaux documentation](https://developer.jcdecaux.com/#/opendata/vls?page=dynamic)

