
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


@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    """ Clear selected data if click data is used

    Args:
        clickData (list): selected list

    Returns:
        list : empty list
    """
    if clickData:
        return {"points": []}


@app.callback(Output("total-rides", "children"), [Input("location-dropdown", "value")])

def update_total_rides(value):
    """ Update the total number of buildings in the Label

    Args:
        value (string): name of the city

    Returns:
        int: number of buildings in that city
    """
    cantidad = len(df[df["BARRIO"] == value].index)
    return "TOTAL DE PARCELAS: {0}".format(cantidad)


def update_total_rides_selection(location, selection):
    """ update building labels

    Args:
        location (string): selected city
        selection (list): selected levels

    Returns:
        string: number of items selected overall
    """
    firstOutput = ""

    if selection != None or len(selection) != 0:
        totalInSelection = 0
        for x in selection:
            totalInSelection += len(df[df["NIVELES"] == x].index)

        firstOutput = "Total de elementos seleccionados: {0}".format(totalInSelection)

    if (
        location == None
        or selection == None
        or len(selection) == 24
        or len(selection) == 0
    ):
        return firstOutput, (location, " - Mostrando Nivel: All")

    holder = sorted([int(x) for x in selection])

    if holder == list(range(min(holder), max(holder) + 1)):
        return (
            firstOutput,
            (
                location,
                " - Mostrando Nivel: ",
                holder[0],
                "-",
                holder[len(holder) - 1],
            ),
        )

    holder_to_string = ", ".join(str(x) for x in holder)
    return firstOutput, (location, " - Mostrando Nivel: ", holder_to_string)



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


############ -> FUNCTIONS AND MAP CALLBACKS <- ############

def getLatLonColor(selectedData):
    """ get the coordinates of the selected elements.
        if no items selected show all

    Args:
        selectedData (list): selected items dropwdown

    Returns:
        DataFrame : df of data matching the level
    """
    listCoords = df

    if selectedData == None or len(selectedData) == 0:
        return listCoords
    else:
        list_leveles = df[df["NIVELES"].isin(selectedData)]
        return list_leveles



@app.callback(
    Output('map-graph', 'figure'),
    [
        Input("bar-selector", "value"),
        Input("location-dropdown", "value"),
    ],
)
def update_figure(selectedData, selectedLocation):
    """ GRAPHIC MAP
    shows the map graph and updates depending on the selected city.
    shows points of the levels depending on the selection.

    Args:
        selectedData (list): selected items dropwdown or histogram
        selectedLocation (string): city name

    Returns:
        mapbox graph: grafico de mapa
    """
    zoom = 12.0
    latInitial = -34.7509
    lonInitial = -58.5846
    bearing = 0

    if selectedLocation:
        zoom = 12.0
        latInitial = list_of_locations[selectedLocation]["lat"]
        lonInitial = list_of_locations[selectedLocation]["lon"]

    
    list_Coords = getLatLonColor(selectedData)

    return go.Figure(
        data=[
            # Data of all the buildings according to the level.
            go.Scattermapbox(
                lat = list_Coords["y"],
                lon = list_Coords["x"],
                mode = "markers",
                customdata = list_Coords[["BARRIO", "PADRON","DIF_PADRON","SUP_PARCEL", "PER_PARCEL"]],
                hovertemplate = '<br>'.join([
                    'BARRIO: %{customdata[0]}',
                    'PADRON: %{customdata[1]}',
                    'DIF EDIFICACIONES: %{customdata[2]}',
                    'SUPERFICIE PARCELA: %{customdata[3]}',
                    'PERIMETRO PARCELA: %{customdata[4]}',
                ]),
                hoverlabel = dict(namelength=0),
                marker=dict(
                    showscale=True,
                    cmax = 23,
                    cmin = 0,
                    color = list_Coords["NIVELES"],
                    opacity=0.5,
                    size=5,
                    colorscale=[
                        [0, "#F4EC15"],
                        [0.04167, "#DAF017"],
                        [0.0833, "#BBEC19"],
                        [0.125, "#9DE81B"],
                        [0.1667, "#80E41D"],
                        [0.2083, "#66E01F"],
                        [0.25, "#4CDC20"],
                        [0.292, "#34D822"],
                        [0.333, "#24D249"],
                        [0.375, "#25D042"],
                        [0.4167, "#26CC58"],
                        [0.4583, "#28C86D"],
                        [0.50, "#29C481"],
                        [0.54167, "#2AC093"],
                        [0.5833, "#2BBCA4"],
                        [1.0, "#613099"],

                    ],
                    colorbar=dict(
                        title="niveles",
                        x=0.93,
                        xpad=0,
                        nticks=24,
                        tickfont=dict(color="#d8d8d8"),
                        titlefont=dict(color="#d8d8d8"),
                        thicknessmode="pixels",
                    ),
                ),
            ),

            go.Scattermapbox(
                lat=[list_of_locations[i]["lat"] for i in list_of_locations],
                lon=[list_of_locations[i]["lon"] for i in list_of_locations],
                mode="markers",
                hoverinfo="text",
                text=[i for i in list_of_locations],
                marker=dict(size=8, color="#ffa0a0"),
            )
        ],

        layout = Layout(
            autosize = True,
            margin = go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend = False,
            mapbox = dict(
                accesstoken = mapbox_access_token,
                center = dict(lat=latInitial, lon=lonInitial),
                style = "dark",
                bearing = bearing,
                zoom = zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 12,
                                        "mapbox.center.lon": "-58.5846",
                                        "mapbox.center.lat": "-34.7509",
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )



if __name__ == '__main__':
    app.run_server(debug=True)


