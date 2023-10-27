# external
import numpy
import pandas
# standard
import json
import os
import random
import re

def haversine(x: float) -> float:
    return numpy.sin(x/2)**2

def haversine_distance(latitude1_deg: float, longitude1_deg: float, latitude2_deg: float, longitude2_deg: float, radius_km: float = 6378) -> float:
    """
    Calculate distance between two geographical points given in degrees.
    https://en.wikipedia.org/wiki/Haversine_formula 
    """
    latitude1_rad, longitude1_rad, latitude2_rad, longitude2_rad = numpy.radians([
        latitude1_deg,
        longitude1_deg,
        latitude2_deg,
        longitude2_deg])

    latitude_difference = latitude1_rad - latitude2_rad
    longitude_difference = longitude1_rad - longitude2_rad
    
    haversine_theta = haversine(latitude_difference) + numpy.cos(latitude1_rad) * numpy.cos(latitude2_rad) * haversine(longitude_difference)
    distance = 2 * radius_km * numpy.arcsin( numpy.sqrt(haversine_theta) )
    return distance


def trim_for_boxplot(values: pandas.core.series.Series | list, length: int = 1000) -> list:
    """
    Keep 10% of most extreme values from each tail and select a number of values randomly from the rest
    """
    values = sorted(list(values))
    n_values_to_keep = length if len(values) > length else len(values)
    n_tail_values = int(n_values_to_keep * 0.1)
    values_to_keep = (
        values[:n_tail_values] + 
        random.sample(values[n_tail_values:-n_tail_values], n_values_to_keep - 2 * n_tail_values) + 
        values[-n_tail_values:])
    return values_to_keep


def get_pdf_values(values: list | pandas.core.series.Series) -> tuple[numpy.ndarray, numpy.ndarray]:
    """
    Get numpy histogram with resolution based on interquantile range.
    Used to plot a probability density function (PDF)
    First value in return tuple gives the edges of bins (PDF x values).
    Second value in return tuple gives the number of data points in each bin (PDF y values).
    """
    # Set resolution
    n_bins_in_interquantile_range = 50

    values = pandas.Series(values)
    values_range = values.max() - values.min()
    values_interquantile_range = values.quantile(0.75) - values.quantile(0.25)

    n_bins = int(values_range / (values_interquantile_range / n_bins_in_interquantile_range))
    histogram = numpy.histogram(values, bins=n_bins, density=True)

    return (histogram[1], histogram[0])


def parse_input_file_line(line: str, parse_value: bool = True) -> (str, (dict | list | str)):
    """
    Parse line from input file.
    Returns None, if it's a comment line (starting with #).
    Tries to parse value: dict if value is json, list if it's values separated by commas, string otherwise.
    :param line: Line from readlines
    :param parse_value: True/False whether values should be automatically parsed
    :return: None if comment line,
    else variable name + dict if json, list if comma separated values, string if single value.
    """
    if re.search(r"^\s*#", line) or not re.search(r"=", line):
        return
    else:
        name = line.split("=")[0].strip()
        value = line.split("=")[1].strip()
    if parse_value:
        try:
            value = json.loads(value)
        except json.decoder.JSONDecodeError:
            value = [list_item.strip() for list_item in value.split(",")]
            value = value[0] if len(value) == 1 else value      # return str if only a single value, else list
    return name, value


def parse_input_file(path: str, parse_values: bool = True,
                     set_environmental_variables: bool = False) -> (None, dict):
    """
    Parse values from .env or .ini file.
    Optionally set values straight to environment without returning.
    :param path: Path to file that is to be imported.
    :param parse_values: True/False - attempt to parse parameter value to list / dict.
    :param set_environmental_variables: True/False - set imported variables directly to environment without returning.
    :return: A dict on imported values or None, if set straight to environmental variables.
    """
    parsed_values = dict()
    with open(path) as input_file:
        for line in input_file.readlines():
            parsed_line = parse_input_file_line(line, parse_values)
            if parsed_line is not None:
                parsed_values[parsed_line[0]] = parsed_line[1]
    if set_environmental_variables:
        # Make sure values are strings (env variables only accept strings)
        env_variables = {key: str(value) for key, value in parsed_values.items()}
        os.environ.update(**env_variables)
    return parsed_values