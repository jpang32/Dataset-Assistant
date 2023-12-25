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


def format_file_metadata(file_metadata: dict) -> dict:
    raw_columns = file_metadata["codeBook"]["dataDscr"]["var"]
    if type(raw_columns) == dict:
        raw_columns = [raw_columns]
    result_columns = []

    for raw_column in raw_columns:
        result_column = {}
        result_column["name"] = raw_column["@name"]

        column_type = raw_column["varFormat"]["@type"]
        if column_type == "numeric":
            sum_stat = raw_column.get("sumStat", [])
            acceptable_sum_stat_keys = ["max", "min", "mode", "medn", "mean", "stdDev"]
            for stat in sum_stat:
                if stat["@type"] in acceptable_sum_stat_keys:
                    result_column[stat["@type"]] = stat["#text"]

            if raw_column["@intrvl"] == "continuous":
                result_column["type"] = "float"
            else:
                if sum_stat and all(x in ['0.0', '1.0'] for x in [result_column["max"], result_column["min"], result_column["mode"], result_column["medn"]]):
                    result_column["type"] = "bool"
                else:
                    result_column["type"] = "int"

        elif column_type == "character":
            category = raw_column["varFormat"].get("@category")
            if category == "date":
                result_column["type"] = "date"
            elif category == "time":
                result_column["type"] = "time"
            else:
                result_column["type"] = "str"

        if "type" not in result_column:
            result_column["type"] = "other"

        result_columns.append(result_column)


    return {
        "columns": result_columns,
    }


def main(title_search_terms: list):
    result = []
    directory_count = 0

    for title_search_term in title_search_terms:
        search_results = search_dataverse_for_datasets(title_search_term)
        for item in search_results:
            dataset_id, version_id = get_dataset_id_and_version_id(item["global_id"])
            file_ids = get_file_ids_from_dataset(dataset_id, version_id)

            formatted_file_metadata_list = []
            retrieved_all_file_metadata_for_dataset = True
            for file_id in file_ids:
                try:
                    file_metadata = get_file_metadata(file_id)
                except Exception as e:
                    retrieved_all_file_metadata_for_dataset = False
                    print(f"get_file_metadata failed: {e}.\n Skipping over this "
                          f"dataset.")
                    break
                formatted_file_metadata = format_file_metadata(file_metadata)
                formatted_file_metadata_list.append(formatted_file_metadata)

            # if retrieved_all_file_metadata_for_dataset:
            #     if os.path.exists(f"../data/{directory_count}"):
            #         os.system(f"rm -rf ../data/{directory_count}")
            #     else:
            #         os.system(f"mkdir ../data/{directory_count}")
            #
            #     directory_count += 1

    return result


if __name__ == '__main__':
    title_search_terms = [
        "covid19",
        "weather",
        "medical"
    ]

    main(title_search_terms)
