
# external
import plotly
import pandas

def add_pdf_plot(
        figure: plotly.graph_objs._figure.Figure,
        x_values: (list | pandas.core.series.Series),
        y_values: (list | pandas.core.series.Series),
        color: str,
        cutoffs: tuple[float, float] = (0, 0),
        legend_name: str = None,
        subplot_row: int = None,
        subplot_column: int = None) -> plotly.graph_objs._figure.Figure:
    """
    Add PDF plot to plotly figure.
    Optionally also show cutoffs for outliers and use specified subplot
    """
    pdf_plot = plotly.graph_objects.Scatter(
        x=x_values,
        y=y_values,
        mode="lines",
        name=legend_name,
        line=dict(
            color=color))
    figure = (
        figure
            .add_trace(
                pdf_plot,
                row=subplot_row,
                col=subplot_column)
            .add_vrect(
                x0=cutoffs[0],
                x1=cutoffs[1],
                fillcolor=color,
                opacity=0.2,
                line_width=0,
                row=subplot_row,
                col=subplot_column))
    return figure
