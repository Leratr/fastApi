import psutil
import plotly.graph_objs as go
from dash import Dash, dcc, html, callback, Input, Output
from measurements import update_msts, cpu, CPU_COUNT

dash_app = Dash(__name__, requests_pathname_prefix='/dash/', title='System online')

dash_app.layout = html.Div([
    html.P(id='cpu_text', children=''),
    dcc.Graph(id='cpu_graph'),
    dcc.Interval(id='timer', interval=100)
])

@dash_app.callback(
    [Output('cpu_text', 'children'), Output('cpu_graph', 'figure')],
    [Input('timer', 'n_intervals')]
)
def update(n):
    update_msts()

    cpu_traces = []
    for i in range(CPU_COUNT):
        cpu_traces.append(
            go.Scatter(
                x=list(range(100)),
                y=cpu[i],
                name=f'CPU{i}'
            )
        )

    return f"CPU Load: {psutil.cpu_percent()}%", {'data': cpu_traces}
