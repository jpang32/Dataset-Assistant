import pytest
from src.data_scraper import search_dataverse_for_datasets, get_dataset_id_and_version_id, get_file_ids_from_dataset, get_file_metadata


@pytest.mark.parametrize("title_search_term", ["covid19", "weather", "medical"])
def test_search_dataverse_for_datasets(title_search_term):
    search_results = search_dataverse_for_datasets(title_search_term)
    assert isinstance(search_results, list)
    assert len(search_results) > 0
    for item in search_results:
        assert "global_id" in item

@pytest.mark.parametrize("title_search_term", ["covid19", "weather", "medical"])
def test_get_dataset_id_and_version_id(title_search_term):
    search_results = search_dataverse_for_datasets(title_search_term)
    for item in search_results:
        dataset_id, version_id = get_dataset_id_and_version_id(item["global_id"])
        assert isinstance(dataset_id, int)
        assert isinstance(version_id, int)

@pytest.mark.parametrize("title_search_term", ["covid19", "weather", "medical"])
def test_get_file_ids_from_dataset(title_search_term):
    search_results = search_dataverse_for_datasets(title_search_term)
    for item in search_results:
        dataset_id, version_id = get_dataset_id_and_version_id(item["global_id"])
        file_ids = get_file_ids_from_dataset(dataset_id, version_id)
        assert isinstance(file_ids, list)
        for file_id in file_ids:
            assert isinstance(file_id, int)

@pytest.mark.parametrize("title_search_term", ["covid19", "weather", "medical"])
def test_get_file_metadata(title_search_term):
    search_results = search_dataverse_for_datasets(title_search_term)
    for item in search_results:
        dataset_id, version_id = get_dataset_id_and_version_id(item["global_id"])
        file_ids = get_file_ids_from_dataset(dataset_id, version_id)
        for file_id in file_ids:
            try:
                file_metadata = get_file_metadata(file_id)
            except Exception as e:
                assert "tabular" in str(e).lower() or "permission" in str(e).lower()
                continue
            assert isinstance(file_metadata, dict)
            assert "fileDscr" in file_metadata["codeBook"]
            assert "dataDscr" in file_metadata["codeBook"]
