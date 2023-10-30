# external
import geojson
import pandas
import plotly.graph_objects
import plotly.subplots
import scipy.stats
import tqdm
# local
import general
import plotting


###############
# Import data #
###############

data_csv_path = "data.csv"
data = pandas.read_csv(data_csv_path)

members = dict(
    name="members",
    color="royalblue")

casual = dict(
    name="casual",
    color="firebrick")


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
data["longitude_delta"] = abs(data["start_lng"] - data["end_lng"])
data["latitude_delta"] = abs(data["start_lat"] - data["end_lat"])
data["direct_distance_km"] = [round(x, 2) for x in map(general.haversine_distance, data["start_lng"], data["start_lat"], data["end_lng"], data["end_lat"])]

# Add speed
data["direct_speed_m_s"] = [round(x, 2) for x in data["direct_distance_km"] * 1000 / data["duration_minutes"] / 60]


##########################
# Ride duration analysis #
##########################

ride_duration_members_raw = data.query("member_casual == 'member'")["duration_minutes"]
ride_duration_casual_raw = data.query("member_casual == 'casual'")["duration_minutes"]


# Plot probability density functions (PDFs) with proposed cutoffs
lower_cutoff = 0
upper_cutoff = max(ride_duration_members_raw.quantile(0.99), ride_duration_casual_raw.quantile(0.99))
ride_duration_members_cutoffs = (lower_cutoff, upper_cutoff)
ride_duration_casual_cutoffs = (lower_cutoff, upper_cutoff)

pdf_raw_figure = plotly.subplots.make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True)

ride_duration_members_pdf_raw = general.get_pdf_values(ride_duration_members_raw)
pdf_raw_figure = plotting.add_pdf_plot(
    figure=pdf_raw_figure,
    x_values=ride_duration_members_pdf_raw[0],
    y_values=ride_duration_members_pdf_raw[1],
    color=members["color"],
    cutoffs=ride_duration_members_cutoffs,
    legend_name=members["name"],
    subplot_row=1,
    subplot_column=1)

ride_duration_members_pdf_raw = general.get_pdf_values(ride_duration_casual_raw)
pdf_raw_figure = plotting.add_pdf_plot(
    figure=pdf_raw_figure,
    x_values=ride_duration_members_pdf_raw[0],
    y_values=ride_duration_members_pdf_raw[1],
    color=casual["color"],
    cutoffs=ride_duration_casual_cutoffs,
    legend_name=casual["name"],
    subplot_row=2,
    subplot_column=1)

pdf_raw_figure.write_html("ride_duration_raw_pdf.html")


# Remove outliers
# Somehow some durations come up negative - will just filter these out
ride_duration_negative = data.query("duration_minutes < 0")

ride_duration_members = ride_duration_members_raw.loc[lambda x: (x >= ride_duration_members_cutoffs[0]) & (x <= ride_duration_members_cutoffs[1])]
ride_duration_casual = ride_duration_casual_raw.loc[lambda x: (x >= ride_duration_casual_cutoffs[0]) & (x <= ride_duration_casual_cutoffs[1])]


# Plot without outliers
pdf_figure = plotly.subplots.make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    row_heights=(0.8, 0.2),
    vertical_spacing=0.05)

ride_duration_members_pdf = general.get_pdf_values(ride_duration_members)
ride_duration_casual_pdf = general.get_pdf_values(ride_duration_casual)

ride_duration_members_pdf_plot = plotly.graph_objects.Scatter(
    x=ride_duration_members_pdf[0],
    y=ride_duration_members_pdf[1],
    mode="lines",
    name=members["name"],
    line=dict(
        color=members["color"]))

ride_duration_casual_pdf_plot = plotly.graph_objects.Scatter(
    x=ride_duration_casual_pdf[0],
    y=ride_duration_casual_pdf[1],
    mode="lines",
    name=casual["name"],
    line=dict(
        color=casual["color"]))

ride_duration_members_box_plot = plotly.graph_objects.Box(
    x=ride_duration_members.sample(10000),
    name=members["name"],
    line=dict(
        color=members["color"]))

ride_duration_casual_box_plot = plotly.graph_objects.Box(
    x=ride_duration_casual.sample(10000),
    name=casual["name"],
    line=dict(
        color=casual["color"]))

pdf_figure.add_traces([ride_duration_members_pdf_plot, ride_duration_casual_pdf_plot], rows=1, cols=1)
pdf_figure.add_traces([ride_duration_members_box_plot, ride_duration_casual_box_plot], rows=2, cols=1)

pdf_figure.write_html("ride_duration_pdf.html")


# Determine if member and casual distributions are different
# Using Mann-Whitney U test
ride_duration_mann_whitney_u_test = scipy.stats.mannwhitneyu(ride_duration_members, ride_duration_casual)
ride_duration_p_value = ride_duration_mann_whitney_u_test[1]


# Bootstrap to simulate change in ride duration if 10% more users are members
conversion_rate = 0.1
n_new_members_converted = int(conversion_rate * len(ride_duration_members))
ride_duration_actual_total = ride_duration_members_raw.sum() + ride_duration_casual_raw.sum()

n_bootstraps = 1000
ride_duration_simulated_totals = list()
for _ in tqdm.tqdm(range(n_bootstraps)):
    ride_duration_members_simulated = pandas.concat([ride_duration_members_raw, ride_duration_members_raw.sample(n_new_members_converted, replace=True)])
    ride_duration_casual_simulated = ride_duration_casual_raw.sample(len(ride_duration_casual_raw) - n_new_members_converted)
    ride_duration_simulated_total = ride_duration_members_simulated.sum() + ride_duration_casual_simulated.sum()
    ride_duration_simulated_totals += [ride_duration_simulated_total]

ride_duration_simulation_differences = ride_duration_simulated_totals - ride_duration_actual_total

simulation_figure = plotly.graph_objects.Figure()
simulation_histogram = plotly.graph_objects.Histogram(x=ride_duration_simulation_differences)
simulation_figure.add_trace(simulation_histogram)

simulation_figure.write_html("ride_duration_simulation.html")


# Map grid
median_deltas = (data
    .query("longitude_delta > 0 & latitude_delta > 0")
    .loc[:,["longitude_delta", "latitude_delta"]]
    .median())

grid_size_multiplier = 0.5
boundaries = (
    (round(data["start_lng"].quantile(0.01), 4), round(data["start_lat"].quantile(0.01), 4)),
    (round(data["start_lng"].quantile(0.99), 4), round(data["start_lat"].quantile(0.99), 4)))

n_squares = (
    round((boundaries[1][0] - boundaries[0][0]) / median_deltas["longitude_delta"] / grid_size_multiplier),
    round((boundaries[1][1] - boundaries[0][1]) / median_deltas["latitude_delta"] / grid_size_multiplier))

grid_size = (
    (boundaries[1][0] - boundaries[0][0]) / n_squares[0],
    (boundaries[1][1] - boundaries[0][1]) / n_squares[1])

############################## Loop over square boundaries and determine how many start points fall in each
############################## Avoid plotting some low quantile of squares


test_points = data[["start_lng", "start_lat"]][:100]
test_points["row_column"] = list(range(100))
test_points["ride_duration"] = 10

geojson_features = list()
for i, row in test_points.iterrows():
    geojson_polygon = geojson.Polygon([[
        (row["start_lng"], row["start_lat"]),
        (row["start_lng"] + 0.01, row["start_lat"]),
        (row["start_lng"] + 0.01, row["start_lat"] + 0.01),
        (row["start_lng"], row["start_lat"] + 0.01),
        (row["start_lng"], row["start_lat"])]])
    geojson_feature = geojson.Feature(
        geometry=geojson_polygon,
        properties={"row_column": row["row_column"]})
    geojson_features += [geojson_feature]

geojson_featurecollection = geojson.FeatureCollection(geojson_features)

fig = plotly.graph_objects.Figure(
    plotly.graph_objects.Choroplethmapbox(
        geojson=geojson_featurecollection,
        locations=test_points.row_column,
        featureidkey="properties.row_column",
        z=test_points.ride_duration,
        colorscale="Viridis",
        zmin=0,
        zmax=12,
        marker_opacity=0.5,
        marker_line_width=0))

fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=8,
    mapbox_center = {"lat": 42.012, "lon": -87.665})

fig.write_html("map.html")



