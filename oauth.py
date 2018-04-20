#!/usr/bin/python3

import json
import os
from urllib.request import urlopen
from multiprocessing import Pool
import argparse

# Create the argparser
parser = argparse.ArgumentParser()
parser.add_argument("user", help="User from which to download the favourite collections")
parser.add_argument("client_id", help="Your app client ID")
parser.add_argument("client_secret", help="Your app client secret")
args = parser.parse_args()

# Initialize the work variables
client_id = int(args.client_id)
client_secret = args.client_secret
user = args.user
offset = 0
pics_to_download = []
pics_folder = "pics/"

# Get authorization token
URL = "https://www.deviantart.com/oauth2/token?\
grant_type=client_credentials&\
client_id=%d&\
client_secret=%s" % (client_id, client_secret)
response = urlopen(URL)
html = response.read()
token = json.loads(html)["access_token"]
print("Access Token: " + token)

# Check if token works
URL =  " https://www.deviantart.com/api/v1/oauth2/placebo?access_token=%s" %\
    (token)
response = urlopen(URL)
html = response.read()
status = json.loads(html)["status"]

# Get favourite folder ID
URL = " https://www.deviantart.com/api/v1/oauth2/collections/folders?\
access_token=%s&\
calculate_size=1&\
mature_content_true&\
username=%s" % (token, user)
response = urlopen(URL)
html = response.read()
collections = json.loads(html)["results"]
folder_id = collections[0]["folderid"]
number_of_pics = collections[0]["size"]
print("Folder ID: " + folder_id)
print("Number of pics in folder: %d" % number_of_pics)


# Loop on every picture in the folder
is_done = False
while not is_done:
    # Get batch of contents of the folder
    URL = " https://www.deviantart.com/api/v1/oauth2/collections/%s?mature_content=true&username=%s&limit=24&access_token=%s&offset=%d"\
        % (folder_id, user, token, offset)
    response = urlopen(URL)
    html = response.read()
    contents = json.loads(html)
    if not contents["has_more"]:
        is_done = True
    else:
        offset = contents["next_offset"]
    print("Next offset: %d" % offset)

    # Add all the images from the batch to the list of images to download
    for e in contents["results"]:
        pics_to_download.append(e)
    print(len(pics_to_download))

def download_pic(result, pics_folder=pics_folder):
    """Uses the result dict to download and save a picture"""
    try:
        src = result["content"]["src"]
        img = urlopen(src).read()
        file = open(pics_folder + src.split("/")[-1], "wb")
        file.write(img)
        file.close()
    except:
        print("Error")
        pass

nb_processes = 40
with Pool(nb_processes) as p:
    p.map(download_pic, pics_to_download)