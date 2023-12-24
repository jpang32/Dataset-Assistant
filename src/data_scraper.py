import os
import requests
import xmltodict

HARVARD_DATAVERSE_URL = os.getenv("HARVARD_DATAVERSE_URL")
HARVARD_DATAVERSE_TOKEN = os.getenv("HARVARD_DATAVERSE_TOKEN")


def search_dataverse_for_datasets(title_search_term: str) -> list:
    search_url = f"{HARVARD_DATAVERSE_URL}/api/search?q=title:*{title_search_term}*&type=dataset"
    search_response = requests.get(search_url, headers={"X-Dataverse-key": HARVARD_DATAVERSE_TOKEN}).json()
    return search_response["data"]["items"]


def get_dataset_id_and_version_id(global_id: str) -> tuple[int, int]:
    dataset_url = f"{HARVARD_DATAVERSE_URL}/api/datasets/:persistentId/?persistentId={global_id}"
    dataset_response = requests.get(dataset_url).json()
    dataset_id = dataset_response["data"]["id"]
    version_id = dataset_response["data"]["latestVersion"]["versionNumber"]
    return dataset_id, version_id


def get_file_ids_from_dataset(dataset_id: int, version_id: int) -> list:
    files_url = f"{HARVARD_DATAVERSE_URL}/api/datasets/{dataset_id}/versions/{version_id}/files?key={HARVARD_DATAVERSE_TOKEN}"
    files_response = requests.get(files_url).json()
    return [file["dataFile"]["id"] for file in files_response["data"]]


def get_file_metadata(file_id: str) -> dict:
    file_metadata_url = f"{HARVARD_DATAVERSE_URL}/api/access/datafile/{file_id}/metadata/ddi"
    file_metadata_response = requests.get(file_metadata_url)
    if not file_metadata_response.ok:
        raise Exception(f"Failed to get metadata for file {file_id}: {file_metadata_response.text}")
    parsed_metadata_response = xmltodict.parse(file_metadata_response.text)
    return parsed_metadata_response


def main(title_search_terms: list):
    result = []

    for title_search_term in title_search_terms:
        search_items = search_dataverse_for_datasets(title_search_term)
        for item in search_items:
            dataset_id, version_id = get_dataset_id_and_version_id(item["global_id"])
            file_ids = get_file_ids_from_dataset(dataset_id, version_id)
            for file_id in file_ids:
                try:
                    file_metadata = get_file_metadata(file_id)
                except Exception as e:
                    print(f"get_file_metadata failed: {e}.\n Skipping over this "
                          f"dataset.")

    return result


if __name__ == '__main__':
    title_search_terms = [
        "covid19",
        "weather",
        "medical"
    ]

    main(title_search_terms)
