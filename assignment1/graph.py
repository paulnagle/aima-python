import pandas as pd

# Load the Excel file
df = pd.read_excel("~/github/aima-python/assignment1/strategy_performance_latest.xlsx", engine="openpyxl")

grouped = df.groupby("Strategy").agg({
    "Performance": "mean",
    "Win Rate (%)": "mean"
}).reset_index()
import plotly.graph_objects as go

fig = go.Figure()

# Add average performance bars
fig.add_trace(go.Bar(
    x=grouped["Strategy"],
    y=grouped["Performance"],
    name="Average Performance",
    marker_color="indianred"
))

# Add average win rate bars
fig.add_trace(go.Bar(
    x=grouped["Strategy"],
    y=grouped["Win Rate (%)"],
    name="Average Win Rate (%)",
    marker_color="lightsalmon"
))

# Customize layout
fig.update_layout(
    title="Average Performance and Win Rate by Strategy",
    xaxis_title="Strategy",
    yaxis_title="Value",
    barmode="group"
)

fig.show()
