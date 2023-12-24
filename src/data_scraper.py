import os
import requests
import xmltodict

from bs4 import BeautifulSoup
from urllib.parse import quote
from xml.etree import ElementTree as ET

HARVARD_SERVER_URL = os.getenv("HARVARD_SERVER_URL")
HARVARD_DATAVERSE_TOKEN = os.getenv("HARVARD_DATAVERSE_TOKEN")


def main(title_search_terms: list):
    for title_search_term in title_search_terms:
        search_url = f"{HARVARD_SERVER_URL}/api/search?q=title:*{title_search_term}*&type=dataset"
        search_response = requests.get(search_url, headers={"X-Dataverse-key": HARVARD_DATAVERSE_TOKEN}).json()
        search_items = search_response["data"]["items"]

        # For each dataset, call Dataverse API to get information on files within dataset
        # Then, for each file, call Dataverse API to get metadata for file
        # Then end result will be a desctiption of the dataset and a list containing the metadata for each file
        for item in search_items:
            dataset_url = f"{HARVARD_SERVER_URL}/api/datasets/:persistentId/?persistentId={item['global_id']}"
            dataset_response = requests.get(dataset_url).json()
            dataset_id = dataset_response["data"]["id"]
            version_id = dataset_response["data"]["latestVersion"]["versionNumber"]

            files_url = f"{HARVARD_SERVER_URL}/api/datasets/{dataset_id}/versions/{version_id}/files?key={HARVARD_DATAVERSE_TOKEN}"
            files_response = requests.get(files_url).json()
            file_id = files_response["data"][0]["dataFile"]["id"]

            file_metadata_url = f"{HARVARD_SERVER_URL}/api/access/datafile/{file_id}/metadata/ddi"
            file_metadata_response = requests.get(file_metadata_url)
            parsed_metadata_response = xmltodict.parse(file_metadata_response.text)

    return parsed_metadata_response

if __name__ == '__main__':
    title_search_terms = [
        "covid19",
        "weather",
        "medical"
    ]

    main(title_search_terms)