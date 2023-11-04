# 2023-11-05
Could also calculate the effect size for casual -> member conversion. E.g. run simulations by month and normalize by monthly standard deviation.
#idea

# 2023-11-04
HTML boxes can be used to add notes/glossary.

For some reason x axis title appears on top and in the bottom after setting it to appear in the bottom.
Will use plot title instead of axis title for now.
A shared title can be defined by x_title in plotly.subplots.make_subplots - appears bottom center by default

Hid the redundant legends with showlegend=False in trace creation.

Jupyter plan:
2. Plot duration pdf-s
3. Analyse distribution difference
4. Bootstrap the effect


# 2023-11-01
nan values can't be stored as properties in geojson feature. Using None instead.


# 2023-10-31
## Plotting geojson grid
Removed cells that have less than 0.01% of started rides.


# 2023-10-30
## Plotting geojson grid
Using half of median ride distance in each coordinate direction as grid size.
Use 1st to 99th quantile as the total grid area to discard extreme outliers on each side.


# 2023-10-29
## Plotting geojson
Apparently geojson Featurecollection objects can be used directly in plotly.graph_objects.Choroplethmapbox geojson attribute.
Coordinate boundaries seem quite weird for the data set (no major cities - maybe Toronto?).
Somehow the individual coordinates are still in Chicago - probably made some mistake with plotting initially.

mapbox_style="carto-positron" doesn't require mapbox license.

Can't figure out a way to plot geojson points with choroplet mapbox.

Apparently 0.01 units of latitude and 0.01 units of longitude are not the same distance (doesn't make a square).

Have to figure out the range of coordinates and outliers to get a good grid size.


# 2023-10-27
## More ride duration analysis
Plot starting station coordinates and indicate with color, where the longest rides are started from.
Average coordinates to 2 decimal places (~1 km precision).
Compare with direct distance coordinates. Maybe indicates, which locations need more electric bikes?

## Plotting over a map
Can use Plotly scattergeo, but by default it only supports locations up to US states:
https://plotly.com/python/reference/#scattergeo-locationmode

Maybe use square grid with different alphas over a map. Or draw only squares that have more than a threshold of ride starts
Square size - half or third of median ride distance.
Apparently latitude decreases from north to south

## Mapbox
Seems that using Mapbox can give better precision.
https://plotly.com/python/reference/#scattermapbox
https://plotly.com/python/mapbox-density-heatmaps/
https://plotly.github.io/plotly.py-docs/generated/plotly.graph_objects.Densitymapbox.html - might be the correct option - still uses points though
https://python-charts.com/spatial/choropleth-map-plotly/ - probably the correct option - needs some geojson coordinates as input
https://plotly.com/python/mapbox-layers/
Might need token: https://docs.mapbox.com/help/glossary/access-token/ - yes, using default public token

The default Mapbox style requires an API token in order to work, so if you don’t have one you will need to specify any of the styles that not require an API token, which are: ‘open-street-map’, ‘white-bg’, ‘carto-positron’, ‘carto-darkmatter’, ‘stamen-terrain’, ‘stamen-toner’ and ‘stamen-watercolor’.


### Chorepleth map
https://plotly.com/python/mapbox-county-choropleth/ - doesn't need token?


#### Geojson
example: https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json
https://geojson.org/
spec: https://datatracker.ietf.org/doc/html/rfc7946

You will also need to set featureidkey to the geojson identifier (defaults to id and in other case takes the form properties.<key>)
which matches the column name passed to locations.

General geojson file structure

**Feature Object**

   A Feature object represents a spatially bounded thing.  Every Feature
   object is a GeoJSON object no matter where it occurs in a GeoJSON
   text.

   o  A Feature object has a "type" member with the value "Feature".

   o  A Feature object has a member with the name "geometry".  The value
      of the geometry member SHALL be either a Geometry object as
      defined above or, in the case that the Feature is unlocated, a
      JSON null value.

   o  A Feature object has a member with the name "properties".  The
      value of the properties member is an object (any JSON object or a
      JSON null value).

   o  If a Feature has a commonly used identifier, that identifier
      SHOULD be included as a member of the Feature object with the name
      "id", and the value of this member is either a JSON string or
      number.

```json
{
    "type": "FeatureCollection",
    "features": [
        {"type":
            "Feature",
            "properties": {"GEO_ID": "0500000US01083", "STATE": "01", ...},
            "geometry":
                {"type": "Polygon",
                "coordinates": [[ [-86.836306, 34.991764], [-86.820657, 34.991764], [-86.783648, 34.991925], ...]]},
            "id": "01083"},
        ...
    ]
}
```

**Polygon**

   To specify a constraint specific to Polygons, it is useful to
   introduce the concept of a linear ring:

   o  A linear ring is a closed LineString with four or more positions.

   o  The first and last positions are equivalent, and they MUST contain
      identical values; their representation SHOULD also be identical.

   o  A linear ring is the boundary of a surface or the boundary of a
      hole in a surface.

   o  A linear ring MUST follow the right-hand rule with respect to the
      area it bounds, i.e., exterior rings are counterclockwise, and
      holes are clockwise.

   o  For type "Polygon", the "coordinates" member MUST be an array of
      linear ring coordinate arrays.

```json
{
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [100.0, 0.0],
                [101.0, 0.0],
                [101.0, 1.0],
                [100.0, 1.0],
                [100.0, 0.0]
            ]
        ]
    },
    "properties": {
        "prop0": "value0",
        "prop1": {
            "this": "that"
        }
    }
}
```

**Coordinates**

The first two elements are longitude and latitude, or
   easting and northing, precisely in that order and using decimal
   numbers.


**Geojson library**

https://pypi.org/project/geojson/



# 2023-10-26
## Handling outliers
Let's try to find a way to plot the pdf with the supposed cutoff regions highlighted.
Have to find a way to get a good bin size. Try: get IQR and make sure it has 100 bins. Use the same bin size for the rest of the distribution.

Cutoffs at 0 minutes and 99th percentile seems good for ride duration.

Might be a good idea to generalize the function for creating pdf plots with cutoffs.

Try to use the same cutoff for both - the maximum of the two

## Testing distribution difference
It seems that with big enough sample sizes, Mann-Whitney gives a tiny p-value.
I.e. should reject the null-hypothesis that the distributions are the same.
But they look similar and have similar modes etc.
- https://stats.stackexchange.com/questions/44465/how-to-correct-for-small-p-value-due-to-very-large-sample-size
- https://stats.stackexchange.com/questions/125750/sample-size-too-large
- https://stats.stackexchange.com/questions/261031/problem-with-mann-whitney-u-test-for-large-samples
Maybe try to calculate how much would ride duration increase if 10% of casual users were converted to members.
Plotting both on one graph after removing outliers + box plots might give a good idea

## Bootstrapping 10% membership change
random.choices can't be used on a pandas Series. Pandas has its own random choice method.

## Effect of having more members
It seems that average minutes go down for members. Not sure if it's causal.
It would help to know how many rides are by the same persons. I.e. do people start riding more often once they become members.
Could make a graph for what are the values of member engagement that would be worthwhile converting someone to a member.

## Plotting
Change subplots sizes - box plot hight lower

## Analysis by stations and bike types
Find the most popular stations.
Get time series of proportion of electric bikes rented for every hour. 
Might show that there are periods with no electric bikes available.

## Analysis by area
Check if member rides correlate with coordinates. Maybe there are areas where more focus is needed.



# 2023-10-25
## Ride duration analysis
tried creating a boxplot with all points - too much to handle for the computer

tried creating a function to select only 100 outliers + random values from all others.
The selection was very uneven - it looked like outliers start from some specific value

Tried to use a histogram - only has a massive peak in the middle. Have to remove outliers to get a better picture.

Tried using standard deviation to remove outliers fallin outside some multiple of std deviations.
Because of outliers, the standard deviation is really stretched out for one group.

Should use median and interquartile range. By default [Q(0.25) - 1.5 * IQR, Q(0.75) + 1.5 * IQR]  is used.
Maybe I should try to use some better way to find the cutoff point. E.g. find highest derivate between some percentiles.
Too much experimentation - settle with PDF with a rectangle showing the cutoffs for now.

Visually the 1.5*iqr cutoff discards too much data. Let's try cutting off at a value where PDF passes through 0.01.
Problematic, because the value depends on number of histogram bins (i.e. the resolution of the pdf).
If we increase resolution, the cutoff changes.
Also problematic, because one of the series has really big outliers, so it needs a finer resolution to get good cutoff location.
That means the cutoff can't be the same for both series.

Try making the cutoff some proportion of maximum. Also maybe make number of bins dependent on range.

## Negative durations
Don't see any reason or pattern in these values. Will just drop the values.
Might have to investigate later if there is any correlation in the dropped values with other variables.