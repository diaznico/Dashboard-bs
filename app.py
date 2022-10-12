
import pandas as pd
from dash import Dash, dcc, html, Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
import plotly.express as px
import numpy as np

# public access mapbox token.
mapbox_access_token = ""

# database csv.
df = pd.read_csv("data.csv")
# agrupo los niveles y las cantidades de elementos en cada nivel.
df_niveles = df.groupby(['NIVELES']).size().reset_index(name = "cantidad")

app = Dash(__name__)
app.title = "Data"
app._favicon = ("assets\favicon.ico")
server = app.server

# BARRIOS LA MATANZA 
list_of_locations = {
    "Laferrere": {"lat": -34.7381, "lon": -58.5987},
    "San Justo": {"lat": -34.6759, "lon": -58.5558},
    "Gonzales Catan": {"lat": -34.7692, "lon": -58.6487},
    "Isidro Casanova": {"lat": -34.7049, "lon": -58.5872},
    "Rafael Castillo": {"lat": -34.6973, "lon": -58.6311},
    "Ciudad Evita": {"lat": -34.7171, "lon": -58.5291},
    "20 de Junio": {"lat": -34.7764, "lon": -58.7256},
    "Villa Luzuriaga": {"lat": -34.6727, "lon": -58.5944},
    "Virrey del Pino": {"lat": -34.8569, "lon": -58.6646},
}

######## App appearance and content ########
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls.
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.A(
                            html.Img(
                                className="logo",
                                src=app.get_asset_url("logo.png"),
                            ),
                            href="https://data.buenosaires.gob.ar/dataset/",
                        ),
                        html.H2("DATA BUENOS AIRES"),
                        html.P(
                            """Seleccione diferentes niveles de diferencias entre los datos de restitucion y los recibidos de padrones."""
                        ),

                        # Dropdawn barrios.
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown of locations on the map
                                        dcc.Dropdown(
                                            id="location-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_locations
                                            ],
                                            value = "Laferrere",
                                            placeholder="Seleccione un barrio",
                                        )
                                    ],
                                ),

                                # Dropdown levels.
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown select level
                                        dcc.Dropdown(
                                            id="bar-selector",
                                            options=[
                                                {
                                                    "label": str(n),
                                                    "value": n,
                                                }
                                                for n in range(24)
                                            ],
                                            multi=True,
                                            placeholder="Seleccione nivel",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.P(id="total-rides"),
                        html.P(id="total-rides-selection"),
                        html.P(id="date-value"),
                        dcc.Markdown(
                            """
                            Source: [Datasets](https://data.buenosaires.gob.ar/dataset/?groups=administracion-publica)

                            Links: [Apis](https://www.buenosaires.gob.ar/datosabiertos/apis) | [Historias](https://www.buenosaires.gob.ar/datosabiertos/historias)
                            """
                        ),

                        html.Button("Download CSV", id="btn_csv", n_clicks = 0),
                        dcc.Download(id="download-dataframe-csv"),
                    
                    ],
                ),
                # Column for application charts and diagrams
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph"),
                        html.Div(
                            className="text-padding",
                            children=[
                                "Selecciona cualquiera de las barras del para seleccionar los datos por nivel."
                            ],
                        ),
                        dcc.Graph(id="histogram"),
                    ],
                ),
            ],
        )
    ]
)


############ -> HISTOGRAM FUNCTIONS AND CALLBACKS <- ############

def get_selection(selection):
    """ colors histogram bars and highlights selected elements white

    Args:
        selection (list): list of selected items

    Returns:
        array: returns an np.array ([1,2,3])
    """
    xSelected = []
    colorVal = [
        "#F4EC15",
        "#DAF017",
        "#BBEC19",
        "#9DE81B",
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#34D822",
        "#24D249",
        "#25D042",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2AC093",
        "#2BBCA4",
        "#2BB5B8",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4",
        "#3B2FA0",
        "#4E2F9C",
        "#603099",
    ]

    # Put the selected levels into a list of xSelected numbers
    xSelected.extend([int(x) for x in selection])

    for i in range(24):
        # If the bar is selected, color it white
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#FFFFFF"
    return np.array(colorVal)


@app.callback(
    Output("bar-selector", "value"),
    [Input("histogram", "selectedData"), Input("histogram", "clickData")],
)
def update_bar_selector(value, clickData):
    """ histogram data update dropdown values

    Args:
        value (list): multiple selection on histogram
        clickData (list): histogram click data

    Returns:
        list: list without order or indices
    """
    holder = []
    if clickData:
        holder.append(str(int(clickData["points"][0]["x"])))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])))

    for index in range(len(holder)):
        holder[index] = int(holder[index])

    return list(set(holder))


@app.callback(
    Output("histogram", "figure"), 
    [
        Input("location-dropdown", "value"),
        Input("bar-selector", "value")
    ])

def update_bar_chart(nombre_barrio, seleccion):
    """ histogram graph
        update histogram according to the city

    Args:
        nombre_barrio (string): city ​​name
        seleccion (list): selected items dropwdown

    Returns:
        graph : graph histogram
    """
    
    df_filtrado_barrios = df[df['BARRIO'] == nombre_barrio]
    df_niveles = df_filtrado_barrios.groupby(['NIVELES']).size().reset_index(name = "cantidad")

    colorVal = get_selection(seleccion)
    
    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
    )

    return go.Figure(
        data=[
            go.Bar(
                x = df_niveles["NIVELES"], 
                y = df_niveles["cantidad"], 
                marker=dict(color=colorVal), 
                hoverinfo="y", 
                text = df_niveles["cantidad"],
                textposition="outside",
            ),
            
            go.Scatter(
                opacity=0,
                hoverinfo="all",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )

if __name__ == '__main__':
    app.run_server(debug=True)


