# external
import pandas
import plotly.graph_objects
import plotly.subplots
# local
import general
import plotting


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


#########################
# Add derived variables #
#########################

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

members = dict(
    name="members",
    color="royalblue")

casual = dict(
    name="casual",
    color="firebrick")

ride_duration_members = data.query("member_casual == 'member'")["duration_minutes"]
ride_duration_casual = data.query("member_casual == 'casual'")["duration_minutes"]

# Plot probability density functions (PDFs) with proposed cutoffs
ride_duration_members_cutoffs = (0, ride_duration_members.quantile(0.99))
ride_duration_casual_cutoffs = (0, ride_duration_casual.quantile(0.99))

pdf_figure = plotly.subplots.make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True)

ride_duration_members_pdf = general.get_pdf_values(ride_duration_members)
pdf_figure = plotting.add_pdf_plot(
    figure=pdf_figure,
    x_values=ride_duration_members_pdf[0],
    y_values=ride_duration_members_pdf[1],
    color=members["color"],
    cutoffs=ride_duration_members_cutoffs,
    legend_name=members["name"],
    subplot_row=1,
    subplot_column=1)

ride_duration_casual_pdf = general.get_pdf_values(ride_duration_casual)
pdf_figure = plotting.add_pdf_plot(
    figure=pdf_figure,
    x_values=ride_duration_casual_pdf[0],
    y_values=ride_duration_casual_pdf[1],
    color=casual["color"],
    cutoffs=ride_duration_casual_cutoffs,
    legend_name=casual["name"],
    subplot_row=2,
    subplot_column=1)

pdf_figure.write_html("ride_duration_pdf.html")

# Somehow some durations come up negative
# Will just filter these out
ride_duration_negative = data.query("duration_minutes < 0")

#############################################################
# Missing values analysis
# Mann-Whitney to test if casual and subscribed customers differ
