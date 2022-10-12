
import pandas as pd
from dash import Dash, dcc, html, Input, Output

# public access mapbox token.
mapbox_access_token = ""

# database csv.
df = pd.read_csv("data.csv")

app = Dash(__name__)
app.title = "Data"
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



if __name__ == '__main__':
    app.run_server(debug=True)


