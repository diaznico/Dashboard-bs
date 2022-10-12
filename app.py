
import pandas as pd
from dash import Dash, dcc, html, Input, Output

# public access mapbox token.
mapbox_access_token = ""

# database csv.
df = pd.read_csv("data.csv")

app = Dash(__name__)
app.title = "Data"
server = app.server

# App appearance and content
app.layout = html.Div(children=[

    # Dropdown to select levels.
    dcc.Dropdown(
        id = "bar-selector",
        options = [{
            "label" : str(n),
            "value": n,
        } for n in range(24)],
        multi = True,
        placeholder = "Seleccione Nivel"
    ),

    dcc.Graph(id="histogram"),
])


if __name__ == '__main__':
    app.run_server(debug=True)


