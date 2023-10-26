# Introduction

The [LaunchPAD Generic Availability](https://app.swaggerhub.com/apis/Clear-Channel/opendirect-core/1.0.0#/Planning%20Availability/post_avails) endpoint provides generic availability data using a two-step process:

1. A request for availability data is made (with optional date filters). This returns a request ID and an associated endpoint URL 
(Location header) where the availability data can be accessed when it is 
ready.
2. The data endpoint URL is polled until the data is ready, which is returned in a 'Multipart/Mixed' format containing two segments: 
the original request body (step 1) in JSON format, and the retrieved avails 
dataset (in zstandard parquet format)

The script in this repository helps parse and split the 'Multipart/Mixed' response into two separate `.json` and `.zstd.parquet` files.

**Note**: It will take some time (< 5 minutes) to prepare the data for step 2. Querying the endpoint URL earlier than this will 
return a 202. 

```
   +---------+      POST      +------------------+
   |         +--------------->|                  |
1  | Request |                | /avails endpoint |
   |         |<---------------+                  |
   +----+----+      202       +------------------+
        |       <identifier>
        |
        |
        |
        |
   +----+----+      GET       +-------------------------------+
   |         +--------------->|                               |
2  | Request |                | /avails/<identifier> endpoint |
   |         |<---------------+                               |
   |         |      202       |                               |
   |         |<---------------+                               |
   +---------+      200       +-------------------------------+
             multipart/mixed data
```
      

# Setup

## Install dependencies

Create a virtual environment and activate it from this directory

```
python3 -m venv venv
. ./venv/bin/activate
```

Now install all dependencies

```
pip3 install -r requirements.txt
```

## Setup enviroment variables

Create a .env file in the directory of this folder. Use the `example.env` as reference.

## Authorization environment variables

Setup the following variables for the authorization check

```
AUTHENTICATION_ENDPOINT=""
AUTHENTICATION_CLIENT_ID=""
AUTHENTICATION_CLIENT_SECRET=""
```

# Script description

This reads the multipart/mixed API response from the planning avails service and splits it into its .json and .zstd.parquet counterparts.

Usage:

```
python3 multipart_reader.py <filepath_or_url>
```

where `<filepath_or_url>` can either be a filepath to the saved API response on the local filesystem, or a URL to the API response itself. In the latter case the script will perform authorization to get the necessary bearer token before attempting to download the response.

# Auxiliary

## PQRS Parquet File Reader

You can use the PQRS command line tool to inspect parquet files: https://github.com/manojkarthick/pqrs

Example usage:

```
# View first 100 rows
pqrs head -n 100 <parquet_file>

# View schema and row count
pqrs schema <parquet_file>
```
