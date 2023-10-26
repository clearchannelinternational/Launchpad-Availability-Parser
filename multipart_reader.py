import requests
import json
from requests.auth import HTTPBasicAuth
from requests_toolbelt.multipart.decoder import MultipartDecoder
import argparse
import time
from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
load_dotenv()


def get_access_token(url, client, secret):
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials", "client_id": client}
    rsp = requests.post(url, data, auth=HTTPBasicAuth(client, secret), headers=headers)
    if rsp.status_code != 200:
        raise ValueError(f"Invalid credentials - {rsp.status_code}: {rsp.json()}")
    return rsp.json()["access_token"]


def write_split_data(filepath_or_url):
    try:
        path = filepath_or_url
        # deepcode ignore PT: Only used locally
        with open(path, "rb") as f:
            response_content = f.read()
        is_file = True
    except Exception as e:
        is_file = False

    if is_file:
        extracted_boundary = (
            response_content.splitlines()[0].replace(b"--", b"").decode("utf-8")
        )

        rsp = requests.Response()
        rsp.headers["Content-Type"] = f"multipart/mixed;boundary={extracted_boundary}"
        rsp._content = response_content
    else:
        authenticationEndpoint = os.getenv("AUTHENTICATION_ENDPOINT")
        clientId = os.getenv("AUTHENTICATION_CLIENT_ID")
        clientSecret = os.getenv("AUTHENTICATION_CLIENT_SECRET")

        url = filepath_or_url
        access_token = get_access_token(authenticationEndpoint, clientId, clientSecret)

        headers = {"Authorization": "Bearer " + access_token}

        rsp = requests.get(url, headers=headers)

        # Side hack to add boundary to the Content-Type header (as opposed to a separate line) so that it is
        # parsed by the MultipartDecoder library (it only looks within 'Content-Type' header ie it assumes
        # headers are on one line)
        rsp.headers["Content-Type"] += f";boundary={rsp.headers['Boundary']}"

    decoder = MultipartDecoder.from_response(rsp)

    filenames = {}

    for part in decoder.parts:
        headers = part.headers[b"Content-Type"].split(b";")
        content_type = headers[0]

        if content_type == b"application/json":
            jsoncontent = json.loads(part.content.decode())
            filename = f"request_details_{time.time()}.json"
            with open(filename, "w") as f:
                f.write(json.dumps(jsoncontent))
            filenames["request"] = filename

        elif content_type == b"application/octet-stream":
            disposition = part.headers[b"Content-Disposition"]
            filename = disposition.split(b'filename="')[1].split(b'"')[0].decode()
            with open(filename, "wb") as f:
                f.write(part.content)
            filenames["data"] = filename

    return filenames


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("filepath_or_url", type=str, help="Filepath or URL")

    args = parser.parse_args()

    print(write_split_data(args.filepath_or_url))

    print("Complete!")
