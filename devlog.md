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


# 2023-10-26
## Handling outliers
Let's try to find a way to plot the pdf with the supposed cutoff regions highlighted.
Have to find a way to get a good bin size. Try: get IQR and make sure it has 100 bins. Use the same bin size for the rest of the distribution.

Cutoffs at 0 minutes and 99th percentile seems good for ride duration.

Might be a good idea to generalize the function for creating pdf plots with cutoffs.

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
