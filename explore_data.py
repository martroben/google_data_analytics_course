import pandas

data_csv_path = "data.csv"
data = pandas.read_csv(data_csv_path)

# Columns with missing values:
missing_value_columns = data.isnull().any(axis="index")

# Rows with missing values
missing_value_rows = data[data.isnull().any(axis="columns")]


################################
# Check for recoverable values #
################################

# Rounding to 3 decimal places gives ~50 m precision
coordinates_rounding_precision = 3

# Pivot longer
start_columns = [
    "ride_id",
    "rideable_type",
    "member_casual",
    "started_at",
    "start_station_name",
    "start_station_id",
    "start_lat",
    "start_lng"]

end_columns = [
    "ride_id",
    "rideable_type",
    "member_casual",
    "ended_at",
    "end_station_name",
    "end_station_id",
    "end_lat",
    "end_lng"]

data_start = (
    data
        .loc[:, start_columns]
        .rename(columns={col_name: col_name.replace("start_", "") for col_name in start_columns})
        .rename(columns={"started_at": "time"}))
data_start["start_end"] = "start"

data_end = (
    data
        .loc[:, end_columns]
        .rename(columns={col_name: col_name.replace("end_", "") for col_name in end_columns})
        .rename(columns={"ended_at": "time"}))
data_end["start_end"] = "end"

data_tidy = pandas.concat([data_start, data_end])

# Combine coordinates
data_tidy.insert(
        loc=7,
        column="coordinates",
        value=[(round(latitude, coordinates_rounding_precision), round(longitude, coordinates_rounding_precision))
               for latitude, longitude in zip(data_tidy["lat"], data_tidy["lng"])])

data_tidy = (
    data_tidy
        .drop(["lat", "lng"], axis="columns")
        .sort_values(by=["ride_id", "time"])
)

# Get station coordinates
locations_reference = (
    data_tidy
        .loc[:, ["station_name", "station_id", "coordinates"]]
        .dropna(subset="station_name")
        .drop_duplicates()
        .sort_values("station_name"))




################################## Join values and keep ones where they replace None values
data_tidy.join()


start_station_recoverable = (
    (data_tidy["start_station_name"].isna() | data_tidy["start_station_id"].isna()) &
    data_tidy["start_coordinates"].isin(locations_reference["coordinates"]))

end_station_recoverable = (
    (data_tidy["end_station_name"].isna() | data_tidy["end_station_id"].isna()) &
    data_tidy["end_coordinates"].isin(locations_reference["coordinates"]))

data_tidy[start_station_recoverable]
data_tidy[end_station_recoverable]
