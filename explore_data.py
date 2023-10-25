# external
import numpy
import pandas
import plotly.graph_objects
import plotly.subplots
# local
import general


###############
# Import data #
###############

data_csv_path = "data.csv"
data = pandas.read_csv(data_csv_path)


##########################
# Analyze missing values #
##########################

# Columns with missing values:
missing_value_columns = data.isnull().any(axis="index")

# Rows with missing values
missing_value_rows = data[data.isnull().any(axis="columns")]

# Rows with missing end location
missing_end_coordinates = data[data[["end_lat", "end_lng"]].isnull().any(axis="columns")]

# ...
# Somehow some durations come up negative


##############################################
# Analyze member and casual user differences #
##############################################

# Add ride durations
data[["started_at", "ended_at"]] = data[["started_at", "ended_at"]].astype("datetime64[ns]")
data["duration_minutes"] = [round(timedelta.total_seconds() / 60, 2) for timedelta in data["ended_at"] - data["started_at"]]

# Add hour of day
data["start_hour"] = [dt.hour for dt in data["started_at"]]

# Add ride direct distances
data["direct_distance_km"] = [round(x, 2) for x in map(general.haversine_distance, data["start_lat"], data["start_lng"], data["end_lat"], data["end_lng"])]

# Add speed
data["direct_speed_m_s"] = [round(x, 2) for x in data["direct_distance_km"] * 1000 / data["duration_minutes"] / 60]


##########################
# Ride duration analysis #
##########################

members_ride_duration = data.query("member_casual == 'member'")["duration_minutes"]
casual_ride_duration = data.query("member_casual == 'casual'")["duration_minutes"]

# Pdfs
n_bins = 10000
casual_histogram = numpy.histogram(casual_ride_duration, bins=n_bins, density=True)
members_histogram = numpy.histogram(members_ride_duration, bins=n_bins, density=True)

casual_pdf_plot = plotly.graph_objects.Scatter(
    x=casual_histogram[1],
    y=casual_histogram[0],
    mode="lines",
    name="casual",
    line=dict(
        color="firebrick"))

casual_interquantile_range = casual_ride_duration.quantile(0.75) - casual_ride_duration.quantile(0.25)
casual_outliers_cutoffs = (
    casual_ride_duration.quantile(0.25) - 1.5 * casual_interquantile_range,
    casual_ride_duration.quantile(0.75) + 1.5 * casual_interquantile_range)

members_pdf_plot = plotly.graph_objects.Scatter(
    x=members_histogram[1],
    y=members_histogram[0],
    mode="lines",
    name="members",
    line=dict(
        color="royalblue"))

members_interquantile_range = members_ride_duration.quantile(0.75) - members_ride_duration.quantile(0.25)
members_outliers_cutoffs = (
    members_ride_duration.quantile(0.25) - 1.5 * members_interquantile_range,
    members_ride_duration.quantile(0.75) + 1.5 * members_interquantile_range)

pdf_plot_figure = plotly.subplots.make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True)

pdf_plot_figure.add_trace(casual_pdf_plot, row=1, col=1)
pdf_plot_figure.add_vrect(
    x0=casual_outliers_cutoffs[0],
    x1=casual_outliers_cutoffs[1],
    fillcolor="firebrick",
    opacity=0.2,
    line_width=0,
    row=1,
    col=1)

pdf_plot_figure.add_trace(members_pdf_plot, row=2, col=1)
pdf_plot_figure.add_vrect(
    x0=members_outliers_cutoffs[0],
    x1=members_outliers_cutoffs[1],
    fillcolor="royalblue",
    opacity=0.2,
    line_width=0,
    row=2,
    col=1)

pdf_plot_figure.write_html("pdf_outliers.html")

#############################################################
# Missing values analysis
# Mann-Whitney to test if casual and subscribed customers differ
