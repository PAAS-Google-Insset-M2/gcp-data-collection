# Self-service bicycles - Gcp-data-collection

<small>Bicycles in self-service. (Service de Vélo lib in French)</small>

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

This project is part of the red thread project for the PAAS Google course that I've been taking preparing my master's
degree in
Cloud Computing. <br/>

This part focuses on collecting the data and storing it in a bucket on GCP (Google Cloud Platform). After collection,
the data will be
processed (filtering, ...) and used for training an AI model.

The purpose of the entire project is to create an AI based app that will be able to predict the "affluence" of people in
a station
and the availability of the bicycles in a station. It will advise its users whether they should wait for a bicycle or
should go and check another at station.

We are focusing on the stations in Amiens (45098, France). The service is named **Velam**.

For this part I am using python as programming language.

We are using the [JCDecaux API](https://developer.jcdecaux.com/#/opendata/vls?page=getstarted) for the data on the velo
lib stations.

> For calling their API, you have to use the following request with the corresponding
> information: ```GET https://api.jcdecaux.com/vls/v1/stations?contract={contract_name}&apiKey={api_key}``` <br/>
> For the ***contract_name*** variable, the accepted values are listed
> at [contracts](https://developer.jcdecaux.com/#/opendata/vls?page=static) <br/>
> To have the list of all the
> contracts: ```curl https://api.jcdecaux.com/vls/v1/contracts?apiKey={api_key} > contracts.json ``` <br/>
> For the ***api_key*** variable, you have to create an account on their page, and you will receive an API key which you
> should use. <br/>
> For more information, please feel free to
> check: [JCDecaux](https://developer.jcdecaux.com/#/opendata/vls?page=getstarted)

## Authentication on gcloud

For the local development, I had to set up user's credentials. <br />

* Install and initialize the gcloud cli
    ```shell 
      # I am on fedora workstation 38
      sudo dnf install google-cloud-cli  # install
  
      gcloud init  # initialize
  
      gcloud config set project paas-gcp-insset-2023  # change the project
    ```
* Create credential file (ADC - Application Default Credentials)
    ```shell 
      gcloud auth application-default login
    ```

## Needed APIs

* Cloud Resource Manager [cloudresourcemanager.googleapis.com]
* Cloud Storage [storage-component.googleapis.com ] (It is enabled by default, so no need to enable it.)
* Pub/Sub API [pubsub.googleapis.com]
* Artifact Registry [artifactregistry.googleapis.com] (for the cloud functions)
* Cloud Logging [logging.googleapis.com] (for the cloud functions)
* Cloud Run [run.googleapis.com] (for the cloud functions)
* Cloud Build [cloudbuild.googleapis.com] (for the cloud functions)
* Eventarc [eventarc.googleapis.com] (for the 2nd generation of cloud functions)
* Cloud Functions [cloudfunctions.googleapis.com]
* Cloud Scheduler [cloudscheduler.googleapis.com]

To enable the APIs, run the following command line:

```shell
gcloud services enable cloudresourcemanager.googleapis.com pubsub.googleapis.com artifactregistry.googleapis.com\
 logging.googleapis.com run.googleapis.com cloudbuild.googleapis.com eventarc.googleapis.com \
  cloudfunctions.googleapis.com cloudscheduler.googleapis.com
```

## Cloud Storage (Bucket)

A bucket is ...

While creating one, we can specify the project, the location and the storage class.

My bucket name is: ***velo-lib-amiens*** <br/>
I chose the location: ***EUROPE-WEST9*** (located in Paris) which is the closest location to where JCDecaux stores their
data.
Plus, it has low carbon emission and is also the closest to me (who is currently the user). <br/>
I chose the ***standard*** storage class. I thought it would be the best because, I am going to use it after for
training the model, so I will be accessing the data more often.

The command line to create a bucket is the following.

```shell 
# If you have multiple projects, you have to specify the project ID
# gcloud storage buckets create gs://<bucket_name> --project=<project_id> --default-storage-class=<storage_class> --location=<location> --uniform-bucket-level-access

# I have a configuration file with my default project so I use it to fill the project variable. 
gcloud storage buckets create gs://velo-lib-amiens --project=$(gcloud config get-value core/project) --default-storage-class=STANDARD --location=europe-west9 --uniform-bucket-level-access
```

## CLoud Pub/Sub

The Pub/Sub service is ...

For the data collection, we will use it to trigger the function that will fetch the data.

To use it, you have to enable the API which I did earlier.

```shell
# Create topic with the desired id (a string)
# gcloud pubsub topics create <id_topic>
gcloud pubsub topics create velo-lib-amiens-topic

# Create a subscription with the desired id and attach it to the created topic using its id
# gcloud pubsub subscriptions create <subscription_name> --topic=<created_topic_id>
gcloud pubsub subscriptions create velo-lib-amiens-sub --topic=velo-lib-amiens-topic

# Receive messages from the subscription
# gcloud pubsub subscriptions pull <sub_id> --auto-ack
```

## Cloud Function

A cloud function is a serverless execution environment for building and connecting cloud services. With these you write
simple, single-purpose functions that are attached to events emitted from your cloud infrastructure
and services. Your function is triggered when an event being watched is fired, or by an HTTP request.

We are creating a function triggered by a pub/sub topic. It will be triggered when the subscription will send a message.

We will use the function to fetch the data and store it in the bucket.

You also need to enable the API and the ones that it needs to run. While enabling the cloud function API, if you did not
enable the dependant APIs, it will be asked to you whether you want to enable them or not.

I advise you to accept. It will not work either way.

They are multiple parameters that you can specify. I will explain what are the ones that I specified.

* ```--gen2``` to create gen 2 cloud functions
* ```--runtime``` the function programming language
* ```--region``` the region where the cloud function will be deployed
* ```--source``` the source code of the cloud function
* ```--memory``` the memory taken by the cloud function
* ```--entry-point``` the entry point function of the cloud function (the main function)
* ```--trigger-topic``` the trigger of the cloud function (which is a pub/sub topic)
* ```--env-vars-file``` the file containing the environment variables (I specified it because I am using them)
* ```--retry``` it specified that the function must run again if it does not work once

```shell
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

# Triggering the function using the pub/sub topic
# I am not using the message, so it does not matter what it is
gcloud pubsub topics publish velo-lib-amiens-topic --message="Friend"

# See the logs of a cloud function
# gcloud functions logs read --gen2 --region=<region> <function_name> > func_logs.txt
gcloud functions logs read --gen2 --region=europe-west9 python-get-velo-lib-data-function

# Delete an existing function
# gcloud functions delete <function_name> --gen2 --region <region>
gcloud functions delete python-get-velo-lib-data-function --gen2 --region europe-west9
```

## Cloud Scheduler

Cloud Scheduler is a fully managed cron job scheduler. It allows you to schedule virtually any job,
including cloud jobs, cloud infrastructure operations, and more.

You also need to enable the API if you did not earlier.

We will create a scheduler with a pub/sub as a target because it is the one that is triggering the function for fetching
the data.

I chose the location ***europe-west3*** (Belgium) because the scheduler is not available in the ***europe-west9*** (
Paris) location.

The scheduler will run the pubsub sending message line every ***one*** minute.

```shell
# Create a scheduler with a pubsub target - It launches every minute
# gcloud scheduler jobs create pubsub <scheduler_name> --location=<location> --schedule="* * * * *" --topic=<topic_id> --message-body=<message>

gcloud scheduler jobs create pubsub velo-lib-amiens-job --location=europe-west3 --schedule="* * * * *" --topic=velo-lib-amiens-topic --message-body="Friend"
```

To calculate the schedule parameter value:

```shell
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of the month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │                                   7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * * <command to execute>
```

<small> <em><u>Source:</u> <a href="https://en.wikipedia.org/wiki/Cron#Overview">CRON by Wikipedia</a> </em> </small>

### Deploy the project (Cost)

The cost ...

### Contact

Sharonn - [LinkedIn]() <br />
Project
link: [https://github.com/PAAS-Google-Insset-M2/gcp-data-collection](https://github.com/PAAS-Google-Insset-M2/gcp-data-collection)

<!-- ACKNOWLEDGMENTS -->

### Acknowledgments

Helpful resources!

* [Create bucket on GCP](https://cloud.google.com/storage/docs/creating-buckets#create_a_new_bucket)
* [Deploy function](https://cloud.google.com/functions/docs/create-deploy-gcloud)
* [JCDecaux documentation](https://developer.jcdecaux.com/#/opendata/vls?page=dynamic)
* [JCDecaux](https://www.jcdecaux.fr/nous-connaitre)
* [CRON Overview](https://en.wikipedia.org/wiki/Cron#Overview)

