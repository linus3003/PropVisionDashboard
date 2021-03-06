#experimental pie chart

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import feedparser
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import numpy as np
from numpy import random
import datetime
import joblib

external_stylesheets = [
    dbc.themes.FLATLY]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])  # , external_stylesheets=external_stylesheets)

server = app.server

model = joblib.load("resources/model2.joblib")

df = pd.read_csv('resources/dashdata.csv', index_col=0)
df = df[df['price'].notna()]
df = df[df['sqft'].notna()]

# remove invalid points outside Germany
df = df.loc[(df['longitude'] <= 15.58) & (df['longitude'] >= 5.58)]
df = df.loc[(df['latitude'] <= 55.05) & (df['latitude'] >= 47.25)]

# insert slight variation to longitude/latitude to display units of same adress

df['longitude'] = [x + random.choice([i for i in range(-10, 10) if i != 0]) / 1000000 for x in df['longitude']]
df['latitude'] = [x + random.choice([i for i in range(-10, 10) if i != 0]) / 1000000 for x in df['latitude']]

# create scale for size of markers
df_diffq = (df["price"].max() - df["price"].min()) / 16
df["scale"] = (df["price"] - df["price"].min()) / df_diffq + 1

# create EUR per sqm ('sqm' is acutally size in m²)
df['Eur/m²'] = round(df['price'] / df['sqft'])

# remove invalid points with wrong Eur/m²
df = df.loc[(df['Eur/m²'] >= 2500) & (df['Eur/m²'] <= 25000)]

# lists for prediction

wohntypen = df['Wohntyp'].unique()
wohntypendf = pd.DataFrame(wohntypen, columns=['c'])
wohntypendf = wohntypendf.dropna().sort_values('c')

regions = df['region'].unique()
regiondf = pd.DataFrame(regions, columns=['c'])
regiondf = regiondf.dropna().sort_values('c')

dev_states = df['dev_status'].unique()
dev_statesdf = pd.DataFrame(dev_states, columns=['c'])
dev_statesdf = dev_statesdf.dropna().sort_values('c')

# add navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Service 1", href="#"),
                dbc.DropdownMenuItem("Service 2", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="Services",
        ),
        dbc.NavItem(dbc.NavLink("Profile", href="#")),
        # dd space between links an logout button
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem(dbc.NavLink(" ")),
        dbc.NavItem([dbc.Button("Logout", href="#")]),
    ],
    style={'margin': 0, 'margin-right': 0, 'width': '100%'},
    brand="PropVision",
    brand_href="#",
    color="primary",
    dark=True

)
# add footer
footer = dbc.NavbarSimple(
    className="footer",
    children=[
        dbc.NavItem(dbc.NavLink("Privacy", href="#")),
        dbc.NavItem(dbc.NavLink("Imprint", href="#")),
        dbc.NavItem(dbc.NavLink("About", href="#")),
    ],
    style={'margin': '150px 0px 0px 0px', 'width': '100%', "float": "bottom"},
    brand_href="#",
    color="primary",
    dark=True

)

# interactive map
fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color='Eur/m²', hover_name="Name",
                        size=df['scale'], size_max=13,
                        hover_data={"url": False, "price": False, "Wohntyp": True,
                                    "latitude": False, "longitude": False, "scale": False,
                                    "Price": True, "price-pred": False, "Predicted price": True, "sqft": False,
                                    "Living space": True, "Eur/m²": True, "Status": True
                                    },
                        color_continuous_scale=px.colors.diverging.Portland, zoom=4, mapbox_style='carto-positron',
                        opacity=1, custom_data=["url"])

fig.update_layout(
    clickmode='event+select',
    margin=dict(l=0, r=0, t=0, b=0),

)

# histogram
hist = px.histogram(df, x="Eur/m²",
                    title='Histogram of price per m²',
                    labels={'total_bill': 'total bill'},  # can specify one label per df column
                    opacity=0.8, width=350, height=490,
                    # represent bars with log scale
                    color_discrete_sequence=['indianred']  # color of histogram bars
                    )

hist.update_layout(
    margin=dict(l=10, r=20, t=50, b=10),
    paper_bgcolor='rgba(1, 91, 150, 0.05)',
    plot_bgcolor='rgba(1, 91, 150, 0.05)'
)

pc = px.pie(df, values="latitude", names="Wohntyp")  #####

pc.update_layout(
    margin=dict(l=10, r=20, t=50, b=10),
    paper_bgcolor='rgba(1, 91, 150, 0.05)',
    plot_bgcolor='rgba(1, 91, 150, 0.05)'
)

# news sites
# possibility to add more sources
rawrss = [
    'https://www.haufe.de/xml/rss_129130.xml',
]


# updating headlines
def update_news():
    posts = []  # list of posts [(title1, link1) (title2, link2) ... ]
    for url in rawrss:
        feed = (feedparser.parse(url))
        for post in feed.entries:
            posts.append((post.title, post.link))

    ndf = pd.DataFrame(posts, columns=['title', 'link'])
    max_rows = 9
    return html.Div(className="padding-top-10",
                    children=[
                        html.P(
                            className="p-news float-right text-muted margin-left",
                            children=[html.P("Last update : " + datetime.datetime.now().strftime("%H:%M:%S"))],
                        ),
                        html.Div(
                            className="p-news",
                            style={'margin-left': 25}

                        ),

                        html.Table(
                            className="table-news",
                            children=[
                                html.Tr(
                                    children=[
                                        html.Td(
                                            children=[
                                                html.A(

                                                    className="text-info td-link",
                                                    children=ndf.iloc[i]["title"],
                                                    href=ndf.iloc[i]["link"],
                                                    target="_blank",
                                                )
                                            ], style={'border': 'groove', 'border-width': 0.1, 'font-size': '85%',
                                                      'background-color': 'transparent'}
                                        )
                                    ], style={'background-color': 'transparent'}
                                )
                                for i in range(min(len(ndf), max_rows))
                            ],
                            style={'border': 'hidden', 'background-color': 'transparent', 'width': 300,
                                   'margin-left': 25,
                                   'margin-top': 25},
                            # 'border':'solid', 'border-width': 0.1, 'color':'rgba(5, 10, 54,0.7)',
                        ),

                    ],
                    style={'border': 'hidden', 'border-width': 0.1, 'background-color': 'rgba(1, 91, 150, 0.05)',
                           'width': '350 '}

                    ),


# slider years
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

tabs_styles = {
    'height': '44px',
    'width': '150%',
    'margin-right': '0',
    'vertical-align': 'middle',
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '5',
    'margin': dict(l=0, r=0, t=50, b=10),
    'background-color': 'rgba(1, 91, 150, 0.05)'
}

# Layout
app.layout = html.Div([

    html.Div(
        [
            html.Footer([navbar], className='col-12'),

        ], className='row'
    ),

    # content
    # 10 columns div for slider
    html.Div(

        children=[

            html.Div(
                [
                    html.Div(
                        [
                            html.P('Building category'),
                            dcc.Dropdown(
                                id='category-filter',
                                options=[
                                    {'label': i, 'value': i} for i in np.append('All', wohntypendf['c'].unique())

                                ],
                                multi=False,
                                value='All',
                            ),
                        ],
                        className='col-2',
                        style={'display': 'inline-block'}),

                    html.Div(
                        [
                            html.P('Price range in Eur'),
                            dcc.Dropdown(
                                id='price-range',
                                options=[
                                    {'label': 'All', 'value': 'All'},
                                    {'label': '0-250k', 'value': '250k'},
                                    {'label': '250k-500k', 'value': '500k'},
                                    {'label': '500k-1mio', 'value': '1mio'},
                                    {'label': '1mio-1.5mio', 'value': '1.5mio'},
                                    {'label': '1.5-2mio', 'value': '2mio'},
                                    {'label': '>2mio', 'value': '>2mio'}
                                ],
                                value='All',
                                multi=False,
                                searchable=True,
                            )
                        ],
                        className='col-2',
                        style={'display': 'inline-block'}
                    ),

                    html.Div(
                        [
                            html.P('Price range in Eur/m²'),
                            dcc.Dropdown(
                                id='psqm-range',
                                options=[
                                    {'label': 'All', 'value': 'All'},
                                    {'label': '0-7k', 'value': '7k'},
                                    {'label': '7k-14k', 'value': '14k'},
                                    {'label': '>14k', 'value': '>14k'}
                                ],
                                multi=False,
                                value='All'
                            )
                        ],
                        className='col-2',
                        style={'display': 'inline-block'}
                    ),

                    html.Div(
                        [
                            html.P('Size range in m²'),
                            dcc.Dropdown(
                                id='size-range',
                                options=[
                                    {'label': 'All', 'value': 'All'},
                                    {'label': '0-60m²', 'value': '60'},
                                    {'label': '60-120m²', 'value': '120'},
                                    {'label': '120-240m²', 'value': '240'},
                                    {'label': '>240m²', 'value': '>240'}
                                ],
                                multi=False,
                                value='All'
                            )
                        ],
                        className='col-2',
                        style={'display': 'inline-block'}
                    ),

                    html.Div(
                        [
                            html.P('Deviation from pred. price'),
                            dcc.Dropdown(
                                id='predict-range',
                                options=[
                                    {'label': 'All', 'value': 'All'},
                                    {'label': '-20% and less', 'value': '<(20)'},
                                    {'label': '-20% to -10%', 'value': '(20)'},
                                    {'label': '-10% to 0%', 'value': '(10)'},
                                    {'label': '0 to 10%', 'value': '10'},
                                    {'label': '10% to 20%', 'value': '20'},
                                    {'label': '20% and more', 'value': '>20'},

                                ],
                                multi=False,
                                value='All'
                            ),
                        ],
                        className='col-2',
                        style={'display': 'inline-block'}
                    )
                ],
                style={'padding-top': 25, 'padding-bottom': 25, 'margin-left': 40, 'width': '100%'},
                className='row',

            ),
        ],
    ),

    # Map + right-side-panel + newsfeed
    html.Div(
        children=[

            html.Div(
                children=[
                    html.Div(
                        id="map-container",
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
                            ),

                        ], className='col-11',
                    ),

                    dcc.Graph(id="map", figure=fig),

                ], style={'padding-bottom': 15, 'width': '100%'}, className='col-8',
            ),

            dcc.Tabs(
                [

                    dcc.Tab(
                        label='Details',
                        children=[html.Div(id="textcontainer", className="padding-top-10",
                                           children=[html.A(
                                               children="Click on a marker on the map to display its link",
                                               id="link",
                                               href="https://propvision-herokuapp.com",
                                               target="_blank",
                                           )],
                                           style={'fontSize': '12px', 'margin-top': 25})],

                        style=tab_style,
                        className='col-2',

                    ),

                    dcc.Tab(
                        label='Hist',
                        children=[dcc.Graph(id="histogram", figure=hist)],
                        style=tab_style,
                        className='col-2 ',
                    ),
                    dcc.Tab(
                        label='Pie',
                        children=[dcc.Graph(id="pie-chart", figure=pc)],
                        style=tab_style,
                        className='col-2'
                    ),

                    dcc.Tab(
                        label='News',
                        children=[html.Div(id="news", children=update_news())],
                        style=tab_style,
                        className='col-2'
                    ),
                ],
                style=tabs_styles,
            ),

        ], className='row justify-content-center', style={'width': '100%'}

    ),

    html.Div(id='container-price-prediction', children=[
        html.P(className="header-2",
               children="Use our machine learning model to predict the fair price for your building project:"),
        html.Div(children=[
            html.Div(id="container-input", children=[
                html.Label(children="Space in m²"),
                dbc.Input(id="sqft", type="number", placeholder="enter living space in m²"),
                html.Label(children="Rooms"),
                dbc.Input(id="rooms", type="number", placeholder="number of rooms"),
            ]),
            html.Label(children="Status of development"),
            dcc.Dropdown(id='dev_status-dd', className="prediction-dropdown dash-dropdown",
                         options=[{'label': i, 'value': i} for i in dev_statesdf['c'].unique()],
                         multi=False,
                         value='',
                         placeholder="Select development status",
                         ),

            html.Label(children="Living style"),
            dcc.Dropdown(id='wohntyp-dd', className="prediction-dropdown dash-dropdown",
                         options=[{'label': i, 'value': i} for i in wohntypendf['c'].unique()],
                         multi=False,
                         value='',
                         placeholder="Select category",
                         ),
            html.Label(children="Region"),
            dcc.Dropdown(id='region-dd', className="prediction-dropdown dash-dropdown",
                         options=[{'label': i, 'value': i} for i in regiondf['c'].unique()],
                         multi=False,
                         value='',
                         placeholder="Select region",
                         ),

            dbc.Button('Predict', id='submit-val', className="btn-blue", n_clicks=0),
            dbc.Button('reset', id='reset', className="btn-grey", n_clicks=0),

            html.Div(id='container-button-basic',
                     children='Enter a value and press submit'),
        ],

        ),
    ]),

    html.Div(

        [
            html.Div([footer], className='col-12'),

        ], className="row"

    ),

])


@app.callback(
    Output('histogram', 'figure'),
    Input('map', 'selectedData'))
def hist_selected_data(selectedData):
    if selectedData:

        filtList = []
        for i in range(len(selectedData['points'])):
            filtList.append(selectedData['points'][i]['hovertext'])

        filter_df = df[df['Name'].isin(filtList)][['Name', 'Eur/m²']]

    else:
        filter_df = df

    hist = px.histogram(filter_df, x="Eur/m²",
                        title='Distribution of price per m²',
                        labels={'total_bill': 'total bill'},  # can specify one label per df column
                        opacity=0.8, width=350, height=490,
                        # represent bars with log scale
                        color_discrete_sequence=['indianred']  # color of histogram bars
                        )

    hist.update_layout(
        margin=dict(l=10, r=20, t=50, b=10),
        paper_bgcolor='rgba(1, 91, 150, 0.05)',
        plot_bgcolor='rgba(1, 91, 150, 0.05)'
    )

    return hist


# prediction
@app.callback(
    Output('container-button-basic', 'children'),
    [Input('submit-val', 'n_clicks'),
     Input("sqft", "value"),
     Input("rooms", "value"),
     Input("dev_status-dd", "value"),
     Input("wohntyp-dd", "value"),
     Input("region-dd", "value"),

     ])
def update_output(n_clicks, sqft, rooms, devs, wohntyp, region):
    if n_clicks > 0:

        if "Landkreis" in region:
            lk = True
        else:
            lk = False

        d = {'dev_status': [devs], 'sqft': [sqft], 'rooms': [rooms], 'wohntyp': [wohntyp], 'city': [region],
             'is_lk': [lk]}
        test_data = pd.DataFrame(data=d)

        try:
            test_data = test_data.astype({"sqft": float, "rooms": float})

            y = model.predict(test_data)

            out = "€{:,.2f}".format(y[0])
            return out

        except ValueError:
            return 'Unable to give prediction'
    else:
        return 'Enter details of your real estate project'


@app.callback(

    [Output('submit-val', 'n_clicks'),
     Output('sqft', 'value'),
     Output('dev_status-dd', 'value'),
     Output('rooms', 'value'),
     Output('wohntyp-dd', 'value'),
     Output('region-dd', 'value')],

    Input('reset', 'n_clicks'),

)
def reset_input(n_click):
    return 0, "", "", "", "", ""


@app.callback(
    Output('link', 'children'),
    Output('link', 'href'),
    [Input('map', 'clickData')])
def display_click_data(clickData):
    if clickData:

        target = clickData['points'][0]['customdata'][0]
        text = clickData['points'][0]['hovertext']

        return text, target
    else:
        raise PreventUpdate


# callback filter to map
@app.callback(
    Output('map', 'figure'),
    [Input('years-slider', 'value'),
     Input('price-range', 'value'),
     Input('psqm-range', 'value'),
     Input('size-range', 'value'),
     Input('predict-range', 'value'),
     Input('category-filter', 'value'),
     ])
def update_figure(selected_year, price, rel_price, size, diff, cat):
    filtered_df = df[:]

    # sleceted years
    f = "Fertigstellung "
    if (selected_year == 2024):
        filtered_df = filtered_df[filtered_df.dev_status.isin([f + "2020", "Fertiggestellt", f + "2021",
                                                               f + "2022", f + "2023", f + "2024"])]
    elif (selected_year == 2023):
        filtered_df = filtered_df[filtered_df.dev_status.isin([f + "2020", "Fertiggestellt", f + "2021",
                                                               f + "2022", f + "2023"])]
    elif (selected_year == 2022):
        filtered_df = filtered_df[filtered_df.dev_status.isin([f + "2020", "Fertiggestellt", f + "2021",
                                                               f + "2022"])]
    elif (selected_year == 2021):
        filtered_df = filtered_df[filtered_df.dev_status.isin([f + "2020", "Fertiggestellt", f + "2021"])]

    elif (selected_year == 2020):
        filtered_df = filtered_df[filtered_df.dev_status.isin([f + "2020", "Fertiggestellt"])]

    else:
        filtered_df = filtered_df

    # filter prices
    if (price == '250k'):
        filtered_df = filtered_df[filtered_df['price'] <= 250000]

    if (price == '500k'):
        filtered_df = filtered_df[(filtered_df['price'] > 250000) & (filtered_df['price'] <= 500000)]

    if (price == '1mio'):
        filtered_df = filtered_df[(filtered_df['price'] > 500000) & (filtered_df['price'] <= 1000000)]

    if (price == '1.5mio'):
        filtered_df = filtered_df[(filtered_df['price'] > 1000000) & (filtered_df['price'] <= 1500000)]

    if (price == '2mio'):
        filtered_df = filtered_df[(filtered_df['price'] > 1500000) & (filtered_df['price'] <= 2000000)]

    if (price == '>2mio'):
        filtered_df = filtered_df[filtered_df['price'] > 2000000]

    else:
        filtered_df = filtered_df

    # price per sqm filter
    if (size == '60'):
        filtered_df = filtered_df[filtered_df['sqft'] <= 60]

    if (size == '120'):
        filtered_df = filtered_df[(filtered_df['sqft'] > 60) & (filtered_df['sqft'] <= 120)]

    if (size == '240'):
        filtered_df = filtered_df[(filtered_df['sqft'] > 120) & (filtered_df['sqft'] <= 240)]

    if (size == '>240'):
        filtered_df = filtered_df[filtered_df['sqft'] > 240]

    else:
        filtered_df = filtered_df

    # filter size
    if (rel_price == '7k'):
        filtered_df = filtered_df[filtered_df['Eur/m²'] <= 7000]

    if (rel_price == '14k'):
        filtered_df = filtered_df[(filtered_df['Eur/m²'] > 7000) & (filtered_df['Eur/m²'] <= 14000)]

    if (rel_price == '>14k'):
        filtered_df = filtered_df[filtered_df['Eur/m²'] > 14000]

    else:
        filtered_df = filtered_df

    # filter price prediction
    if (diff == '<(20)'):
        filtered_df = filtered_df[(filtered_df['diff_from_prediction'] < -0.2)]

    if (diff == '(20)'):
        filtered_df = filtered_df[
            (filtered_df['diff_from_prediction'] < -0.1) & (filtered_df['diff_from_prediction'] >= -0.2)]

    if (diff == '(10)'):
        filtered_df = filtered_df[
            (filtered_df['diff_from_prediction'] < 0) & (filtered_df['diff_from_prediction'] >= -0.1)]

    if (diff == '10'):
        filtered_df = filtered_df[
            (filtered_df['diff_from_prediction'] > 0) & (filtered_df['diff_from_prediction'] <= 0.1)]

    if (diff == '20'):
        filtered_df = filtered_df[
            (filtered_df['diff_from_prediction'] > 0.1) & (filtered_df['diff_from_prediction'] <= 0.2)]

    if (diff == '>20'):
        filtered_df = filtered_df[(filtered_df['diff_from_prediction'] > 0.2)]


    else:
        filtered_df = filtered_df

    # filter building category

    if cat != 'All':
        filtered_df = filtered_df[filtered_df['Wohntyp'] == cat]
    else:
        filtered_df = filtered_df

    filtered_df = filtered_df.append(
        {'Price': "", 'scale': 0, 'longitude': 9.21, 'latitude': 51.13, 'Name': "This is the center of germany",
         'Predicted price': "", 'Living space': "", 'Status': "", 'Wohntyp': ""}, ignore_index=True)

    fig = px.scatter_mapbox(filtered_df, lat="latitude", lon="longitude", color='Eur/m²', hover_name="Name",
                            size=filtered_df['scale'], size_max=13,
                            hover_data={"url": False, "price": False, "Wohntyp": True,
                                        "latitude": False, "longitude": False, "scale": False,
                                        "Price": True, "price-pred": False,
                                        "Predicted price": True, "sqft": False, "Living space": True,
                                        "Eur/m²": True, "Status": True
                                        },
                            color_continuous_scale=px.colors.diverging.Portland, zoom=4, mapbox_style='carto-positron',
                            opacity=1)

    fig.update_layout(transition_duration=500,
                      margin=dict(l=0, r=0, t=0, b=0))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

