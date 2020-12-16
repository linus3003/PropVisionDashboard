import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from numpy import random
from dash.dependencies import Input, Output


external_stylesheets = [dbc.themes.FLATLY]

df = pd.read_csv('resources/alldata.csv', index_col=0)
df = df[df['price'].notna()]
df = df[df['sqft'].notna()]

# remove invalid points outside Germany
df = df.loc[(df['longitude'] <= 15.58) & (df['longitude'] >= 5.58)]
df = df.loc[(df['latitude'] <= 55.05) & (df['latitude'] >= 47.25)]

#insert slight variation to longitude/latitude to display units of same adress

df['longitude'] =[x + random.choice([i for i in range(-10,10) if i != 0])/1000000 for x in df['longitude']]
df['latitude'] =[x + random.choice([i for i in range(-10,10) if i != 0])/1000000 for x in df['latitude']]

#create scale for size of markers
df_diffq = (df["price"].max() - df["price"].min()) / 16
df["scale"] = (df["price"] - df["price"].min()) / df_diffq + 1


# add navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="PropVision",
    brand_href="#",
    color="primary",
    dark=True

)

#interactive ma
fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color='sqft', hover_name="url", size = df['scale'], size_max=15,
                        color_continuous_scale=px.colors.diverging.Portland, zoom=4, mapbox_style='carto-positron',
                        opacity=1)
# px.colors.diverging.Portland , px.colors.cyclical.IceFire
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0)
)
# histogram
hist = px.histogram(df, x="price",
                    title='Histogram of prices',
                    labels={'total_bill': 'total bill'},  # can specify one label per df column
                    opacity=0.8,
                    # represent bars with log scale
                    color_discrete_sequence=['indianred']  # color of histogram bars
                    )

hist.update_layout(
    margin=dict(l=0, r=0, t=50, b=0),
    paper_bgcolor='rgba(237,240,241,0.8)',
    plot_bgcolor='rgba(237,240,241,0.8)'
)

# styles: open-street-map, white-bg, carto-positron, carto-darkmatter, stamen-terrain, stamen-toner, stamen-watercolor

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])  # , external_stylesheets=external_stylesheets)


# App
app.layout = html.Div(children=[


    html.Div([navbar]),

    html.Div(children=''' Large scale overview on the state of new building projects across Germany. ''',
             style={'marginBottom': 25, 'marginTop': 25, 'marginLeft': 25}
             ),

    html.Div(children=[
        dcc.Dropdown(
            id='filter-dropdown',
            options=[
                {'label': 'Category', 'value': 'NYC'},
                {'label': 'Price', 'value': 'MTL'},
                {'label': 'Units', 'value': 'SF'}
            ],
            # style={'float': 'left','marginBottom': 10, 'width': '45%', 'marginLeft': 25 },
            style={'display': 'inline-block', 'width': '37.5%', 'marginLeft': 25},
            value='NYC'
        ),

        dcc.Dropdown(
            id='filter2-dropdown',
            options=[
                {'label': 'Luxury', 'value': 'NYC'},
                {'label': 'Normal', 'value': 'MTL'},
                {'label': 'Low-end', 'value': 'SF'}
            ],

            # style={'float': 'left','marginBottom': 10, 'width': '45%', 'marginLeft': 25 },
            style={'display': 'inline-block', 'width': '37.5%'},
            value='NYC'
        ),
        dcc.Dropdown(
            id='filter3-dropdown',
            options=[
                {'label': 'Price-Histogram', 'value': 'NYC'},
                {'label': 'Category-Histogram', 'value': 'MTL'},
                {'label': 'Segmentation', 'value': 'SF'}],
            style={'display': 'inline-block', 'width': '20%'},

        )]),
    html.Div(id='dd-output-container'),

    html.Div(
        id="app-container",
        children=[
            html.Div(
                id="left-column",
                children=[
                    html.Div(
                        id="slider-container",
                        children=[
                            html.P(
                                id="slider-text",
                                children="Year of completion: ",
                            ),
                            dcc.Slider(
                                id="years-slider",
                                min=min(YEARS),
                                max=max(YEARS),
                                value=2023,

                                marks={
                                    str(year): {
                                        "label": str(year),
                                        "style": {"color": "primary"},

                                    }
                                    for year in YEARS
                                },

                            )
                        ]
                    )
                ], style={'display': 'inline-block', 'width': '70%'}
            ),

        ], style={'marginBottom': 25, 'marginTop': 25, 'marginLeft': 25, 'marginRight': 25}
    ),

    html.Div(
        id='testcontainer',
        children=[
            dcc.Graph(id='map', figure=fig, style={'display': 'inline-block', 'width': '75%'}),
            dcc.Graph(id='histogram', figure=hist, style={'display': 'inline-block', 'width': '25%'})
        ]
    ),

])


@app.callback(
    Output('map', 'figure'),
    Input('years-slider', 'value'))


def update_figure(selected_year):

    f = "Fertigstellung "

    if (selected_year==2024):
        filtered_df = df[df.dev_status.isin([f + "2020", "Fertiggestellt", f + "2021",
                                              f + "2022", f + "2023", f + "2024"])]
    elif (selected_year==2023):
        filtered_df = df[df.dev_status.isin([f + "2020", "Fertiggestellt", f + "2021",
                                               f + "2022", f + "2023"])]
    elif (selected_year == 2022):
        filtered_df = df[df.dev_status.isin([f + "2020", "Fertiggestellt", f + "2021",
                                               f + "2022"])]
    elif (selected_year == 2021):
        filtered_df = df[df.dev_status.isin([f + "2020", "Fertiggestellt", f + "2021"])]

    elif (selected_year == 2020):
        filtered_df = df[df.dev_status.isin([f + "2020", "Fertiggestellt"])]

    else: filtered_df=df

    fig = px.scatter_mapbox(filtered_df, lat="latitude", lon="longitude", color='sqft', hover_name="url", size=filtered_df['scale'],
                            size_max=15,
                            color_continuous_scale=px.colors.diverging.Portland, zoom=4, mapbox_style='carto-positron',
                            opacity=1)

    fig.update_layout(transition_duration=500,

                      margin=dict(l=0, r=0, t=0, b=0))

    return fig



if __name__ == '__main__':
    app.run_server(debug=True)