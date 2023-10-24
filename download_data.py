# external
import pandas
import requests
import tqdm
# standard
import datetime
import io
from urllib.parse import urljoin
import zipfile

data_base_url = "https://divvy-tripdata.s3.amazonaws.com/"
start_month = "2022_01"
end_month = "2022_12"

months = pandas.date_range(
    start=datetime.datetime.strptime(start_month, "%Y_%m"),
    end=datetime.datetime.strptime(end_month, "%Y_%m") + datetime.timedelta(days=32),
    # Insert a date from next month, because pandas.date_range with freq="M" ^gives last days of month
    freq="M")

file_names = [f"{datetime.datetime.strftime(month, '%Y%m')}-divvy-tripdata" for month in months]

data = list()
for file_name in tqdm.tqdm(file_names):
    response = requests.get(urljoin(data_base_url, f"{file_name}.zip"), allow_redirects=True)
    # ZipFile object accepts file-like objects
    # Use io.BytesIO to turn requests.Response.content to file-like object
    with zipfile.ZipFile(io.BytesIO(response.content)) as data_zipfile:
        zip_file_names = [zip_file.filename for zip_file in data_zipfile.filelist]
        # Some zipped files have a different naming convention
        if f"{file_name}.csv" not in zip_file_names:
            file_name = file_name.replace("tripdata", "publictripdata")
        with data_zipfile.open(f"{file_name}.csv") as data_raw_csv:
            data += [pandas.read_csv(data_raw_csv)]

data_df = pandas.concat(data)

