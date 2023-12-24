import os
import pandas as pd

def clean_data(dataframe: pd.DataFrame):
    pass


def main(data_folder: str):
    # The data folder contains multiple directories
    # Each directory is named with an index
    # Within each directory is a csv file named data.csv
    # Please read each csv file, store it as a pandas dataframe and pass the dataframe as an input to the clean_data function
    # Then, save the output from the clean_data function as metadata.txt in the same directory
    # YOUR CODE HERE:
    for dir_name in os.listdir(data_folder):
        dir_path = os.path.join(data_folder, dir_name)
        if os.path.isdir(dir_path):
            file_path = os.path.join(dir_path, "data.csv")
            df = pd.read_csv(file_path)
            clean_data(df)


if __name__ == '__main__':
    data_folder = "../data/"
    main(data_folder=data_folder)