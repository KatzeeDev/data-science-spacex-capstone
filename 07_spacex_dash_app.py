# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)

launch_sites = spacex_df["Launch Site"].unique()

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        html.Div(
            [
                html.Label("Launch Site:", style={"margin-right": "10px"}),
                dcc.Dropdown(
                    id="site-dropdown",
                    options=[{"label": "All Sites", "value": "ALL"}]
                    + [{"label": site, "value": site} for site in launch_sites],
                    value="ALL",
                    placeholder="Select a Launch Site here",
                    searchable=True,
                ),
            ],
            style={"margin": "20px"},
        ),
        html.Br(),
        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):", style={"margin-left": "20px"}),
        # TASK 3: Add a slider to select payload range
        html.Div(
            [
                dcc.RangeSlider(
                    id="payload-slider",
                    min=0,
                    max=10000,
                    step=1000,
                    marks={i: f"{i}" for i in range(0, 11000, 1000)},
                    value=[min_payload, max_payload],
                    tooltip={"placement": "bottom", "always_visible": True},
                )
            ],
            style={"margin": "20px"},
        ),
        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# TASK 2:
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Success Launches By Site",
        )
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        success_counts = filtered_df["class"].value_counts().reset_index()
        success_counts.columns = ["class", "count"]
        success_counts["class"] = success_counts["class"].map(
            {0: "Failed", 1: "Success"}
        )

        fig = px.pie(
            success_counts,
            values="count",
            names="class",
            title=f"Total Success Launches for {entered_site}",
        )

    return fig


# TASK 4:
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= payload_range[0])
        & (spacex_df["Payload Mass (kg)"] <= payload_range[1])
    ]

    if entered_site == "ALL":
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Correlation between Payload and Success for all Sites",
            labels={"class": "Launch Outcome"},
        )
    else:
        site_filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
        fig = px.scatter(
            site_filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title=f"Correlation between Payload and Success for {entered_site}",
            labels={"class": "Launch Outcome"},
        )

    fig.update_layout(
        yaxis=dict(tickmode="array", tickvals=[0, 1], ticktext=["Failed", "Success"])
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
