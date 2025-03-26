import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, dash_table, no_update
import plotly.graph_objs as go
import pandas as pd
import datetime

# Couleur principale (ici en jaune or)
MAIN_COLOR = "#facd1b"

external_stylesheets = [
    dbc.themes.DARKLY,
    "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "FTSE 100 Price"

# --- Fonctions utilitaires ---
def filter_data_by_date(df, start_date, end_date):
    if start_date is None or end_date is None:
        return df
    try:
        start = datetime.datetime.combine(pd.to_datetime(start_date).date(), datetime.time.min)
        end = datetime.datetime.combine(pd.to_datetime(end_date).date(), datetime.time.max)
    except Exception:
        return df
    return df[(df['time'] >= start) & (df['time'] <= end)]

def get_daily_report():
    now = datetime.datetime.now()
    if now.hour >= 20:
        return "Rapport du jour : Les indicateurs du FTSE 100 sont stables et la performance est excellente."
    else:
        return "Le rapport quotidien sera affiché à 20h."

def is_market_open():
    now = datetime.datetime.now()
    if now.weekday() < 5 and (
        (now.hour > 8 or (now.hour == 8 and now.minute >= 0)) and 
        (now.hour < 16 or (now.hour == 16 and now.minute <= 30))
    ):
        return True
    else:
        return False

def get_market_status_div():
    if is_market_open():
        return html.Div(["Marché : ", html.Span("Ouvert", style={"color": "green", "fontWeight": "bold"})])
    else:
        return html.Div(["Marché : ", html.Span("Fermé", style={"color": "red", "fontWeight": "bold"})])

# --- Boutons Téléchargement & GitHub ---
download_button = dbc.Button(
    "Télécharger CSV", 
    id="download-csv", 
    color="info", 
    style={'backgroundColor': MAIN_COLOR, 'border-color': MAIN_COLOR}
)
download_component = dcc.Download(id="download-dataframe-csv")

github_button = dbc.Button(
    "Accéder au GitHub", 
    href="https://github.com/MxnceHtr/ADVPGL_PRJ",
    target="_blank", 
    style={'backgroundColor': MAIN_COLOR, 'border-color': MAIN_COLOR}
)

# --- Panneau de contrôle ---
control_panel = dbc.Card(
    [
        dbc.CardHeader(html.H4("Contrôles & Options")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    dbc.Button("Rafraîchir", 
                               id="refresh-button", 
                               color="primary",
                               style={'backgroundColor': MAIN_COLOR, 'border-color': MAIN_COLOR}),
                    width=3
                ),
                dbc.Col(
                    dbc.Button("Effacer Filtre", id="clear-filter-button", color="secondary"),
                    width=3
                ),
                dbc.Col(download_button, width=3),
                dbc.Col(github_button, width=3),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(
                    dcc.DatePickerRange(
                        id="date-picker-range",
                        start_date=(datetime.datetime.now() - datetime.timedelta(days=1)).date(),
                        end_date=datetime.datetime.now().date(),
                        display_format='YYYY-MM-DD',
                        style={'backgroundColor': '#ffffff', 'color': '#000000'}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="num-points-dropdown",
                        options=[
                            {"label": "12 points", "value": 12},
                            {"label": "24 points", "value": 24},
                            {"label": "48 points", "value": 48},
                        ],
                        value=48,
                        clearable=False,
                        style={'backgroundColor': '#ffffff', 'color': '#000000'},
                        className="custom-dropdown"
                    ),
                    width=6
                ),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(
                    dbc.RadioItems(
                        id="chart-type-radio",
                        options=[
                            {"label": "Ligne", "value": "line"},
                            {"label": "Barres", "value": "bar"},
                        ],
                        value="line",
                        inline=True,
                        style={'color': '#ffffff'},
                        labelStyle={'color': '#ffffff', 'margin-right': '10px'}
                    ),
                    width=6
                ),
                dbc.Col(
                    dbc.Checklist(
                        options=[{"label": "Échelle Logarithmique", "value": "log"}],
                        value=[],
                        id="log-scale-switch",
                        switch=True
                    ),
                    width=6
                ),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(
                    dbc.Checklist(
                        options=[{"label": "Stop auto-refresh", "value": "stop"}],
                        value=[],
                        id="stop-refresh-switch",
                        switch=True
                    ),
                    width=6
                )
            ]),
        ])
    ],
    className="mb-4 shadow-sm"
)

# --- TITRE CENTRÉ + HEURE + COMPTE À REBOURS + Statut du Marché ---
title_and_time = html.Div(
    [
        html.H1("FTSE 100 Price", style={"textAlign": "center", "color": "#fff"}),
        html.H4(id="current-time", style={"textAlign": "center", "color": "#fff"}),
        html.Div(id="market-status", style={"textAlign": "center", "color": "#fff", "marginTop": "5px"}),
        html.H6(id="countdown-text", style={"textAlign": "center", "color": "#fff", "marginBottom": "20px"}),
    ],
    className="mb-4"
)

# --- Résumé des métriques ---
metrics_card = dbc.Card(
    [
        dbc.CardHeader(
            html.H4("Résumé des Métriques", style={"textAlign": "center", "color": "#ffffff"})
        ),
        dbc.CardBody(
            html.Div([
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-chart-line fa-2x", style={"color": MAIN_COLOR}), width=2),
                    dbc.Col(html.H6("Dernière valeur", className="text-muted mt-2"), width=5),
                    dbc.Col(html.H4(id="last-value", className="text-white mb-0", style={"whiteSpace": "nowrap"}), width=5),
                ], justify="center", className="mb-3"),
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-calculator fa-2x", style={"color": MAIN_COLOR}), width=2),
                    dbc.Col(html.H6("Moyenne", className="text-muted mt-2"), width=5),
                    dbc.Col(html.H4(id="mean-value", className="text-white mb-0", style={"whiteSpace": "nowrap"}), width=5),
                ], justify="center", className="mb-3"),
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-balance-scale fa-2x", style={"color": MAIN_COLOR}), width=2),
                    dbc.Col(html.H6("Médiane", className="text-muted mt-2"), width=5),
                    dbc.Col(html.H4(id="median-value", className="text-white mb-0", style={"whiteSpace": "nowrap"}), width=5),
                ], justify="center", className="mb-3"),
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-ruler-combined fa-2x", style={"color": MAIN_COLOR}), width=2),
                    dbc.Col(html.H6("Écart type", className="text-muted mt-2"), width=5),
                    dbc.Col(html.H4(id="std-value", className="text-white mb-0", style={"whiteSpace": "nowrap"}), width=5),
                ], justify="center", className="mb-3"),
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-percent fa-2x", style={"color": MAIN_COLOR}), width=2),
                    dbc.Col(html.H6("Coeff Variation", className="text-muted mt-2"), width=5),
                    dbc.Col(html.H4(id="cv-value", className="text-white mb-0", style={"whiteSpace": "nowrap"}), width=5),
                ], justify="center", className="mb-3"),
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-arrow-down fa-2x", style={"color": MAIN_COLOR}), width=2),
                    dbc.Col(html.H6("Valeur min", className="text-muted mt-2"), width=5),
                    dbc.Col(html.H4(id="min-value", className="text-white mb-0", style={"whiteSpace": "nowrap"}), width=5),
                ], justify="center", className="mb-3"),
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-arrow-up fa-2x", style={"color": MAIN_COLOR}), width=2),
                    dbc.Col(html.H6("Valeur max", className="text-muted mt-2"), width=5),
                    dbc.Col(html.H4(id="max-value", className="text-white mb-0", style={"whiteSpace": "nowrap"}), width=5),
                ], justify="center", className="mb-3"),
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-expand-arrows-alt fa-2x", style={"color": MAIN_COLOR}), width=2),
                    dbc.Col(html.H6("Étendue", className="text-muted mt-2"), width=5),
                    dbc.Col(html.H4(id="range-value", className="text-white mb-0", style={"whiteSpace": "nowrap"}), width=5),
                ], justify="center", className="mb-2"),
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-wave-square fa-2x", style={"color": MAIN_COLOR}), width=2),
                    dbc.Col(html.H6("Skewness", className="text-muted mt-2"), width=5),
                    dbc.Col(html.H4(id="skew-value", className="text-white mb-0", style={"whiteSpace": "nowrap"}), width=5),
                ], justify="center", className="mb-3"),
            ])
        )
    ],
    className="shadow-sm mb-4"
)

# Nouvelles colonnes attendues (les champs retirés ont été enlevés)
expected_columns = [
    "time", "price", "percentchange", "netchange", "high", "low"
]

# --- Zone principale du contenu ---
content = dbc.Col(
    [
        title_and_time,
        control_panel,
        download_component,
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H4("Graphique en Temps Réel")),
                            dbc.CardBody(
                                dcc.Loading(
                                    dcc.Graph(id="live-graph", config={"displayModeBar": False}),
                                    color=MAIN_COLOR,
                                    type="circle"
                                )
                            )
                        ],
                        className="shadow-sm mb-4",
                    ),
                    width=8
                ),
                dbc.Col(
                    metrics_card,
                    width=4
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4("Rapport Quotidien")),
                        dbc.CardBody(
                            html.Div(id="daily-report", children=get_daily_report())
                        )
                    ],
                    className="shadow-sm mb-4"
                )
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4("Historique des Données")),
                        dbc.CardBody(
                            dash_table.DataTable(
                                id='data-table',
                                columns=[{"name": i, "id": i} for i in expected_columns],
                                data=[],  # Rempli via callback
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'center', 'color': '#ffffff', 'backgroundColor': '#1c1c1c'},
                                style_header={'backgroundColor': '#262626', 'fontWeight': 'bold', 'color': '#ffffff'},
                                filter_action="native",
                                sort_action="native",
                                page_action="native",
                                page_size=10,
                            )
                        )
                    ],
                    className="shadow-sm mb-4"
                )
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H4("Histogramme des Rendements")),
                            dbc.CardBody(
                                dcc.Graph(id="histogram-graph", config={"displayModeBar": False})
                            )
                        ],
                        className="shadow-sm mb-4",
                    ),
                    width=6
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H4("Gauge - Dernière Valeur")),
                            dbc.CardBody(
                                dcc.Graph(id="gauge-graph", config={"displayModeBar": False})
                            )
                        ],
                        className="shadow-sm mb-4",
                    ),
                    width=6
                ),
            ]
        ),
        dcc.Interval(id='interval-component', interval=5 * 60 * 1000, n_intervals=0),
        dcc.Interval(id="countdown-interval", interval=1000, n_intervals=0),
        dcc.Store(id="stored-data"),
        dcc.Store(id="last-refresh-time"),
        dcc.Store(id="next-refresh-time"),
        dbc.Toast(
            id="refresh-toast",
            header="Mise à jour",
            is_open=False,
            duration=3000,
            icon="primary",
            style={"position": "fixed", "top": 10, "right": 10, "width": 350},
        ),
        html.Footer(
            html.Div(id="footer-timestamp", className="text-center text-muted mt-4"),
            className="py-3"
        )
    ],
    width=12,
    style={'padding': '20px'}
)

app.layout = dbc.Container(
    [
        dbc.Row([content], className="g-0")
    ],
    fluid=True,
    style={'backgroundColor': '#0d0d0d'}
)

# --- Callback pour mettre à jour le DatePickerRange selon les dates du CSV ---
@app.callback(
    [Output("date-picker-range", "min_date_allowed"),
     Output("date-picker-range", "max_date_allowed"),
     Output("date-picker-range", "initial_visible_month")],
    [Input("refresh-button", "n_clicks"),
     Input("interval-component", "n_intervals")]
)
def update_date_picker(n_clicks, n_intervals):
    try:
        df = pd.read_csv('./data.csv')
        df.columns = [col.strip().lower() for col in df.columns]
        df['time'] = pd.to_datetime(df['time'])
        min_date = df['time'].min().date()
        max_date = df['time'].max().date()
        return min_date, max_date, max_date
    except Exception:
        return no_update, no_update, no_update

# --- Callback pour stopper l'auto-refresh ---
@app.callback(
    Output('interval-component', 'interval'),
    Input('stop-refresh-switch', 'value')
)
def toggle_auto_refresh(stop_value):
    if "stop" in stop_value:
        return 86400 * 1000  # 24h
    return 5 * 60 * 1000

# --- Callback principal ---
@app.callback(
    [Output('live-graph', 'figure'),
     Output('last-value', 'children'),
     Output('mean-value', 'children'),
     Output('median-value', 'children'),
     Output('std-value', 'children'),
     Output('cv-value', 'children'),
     Output('min-value', 'children'),
     Output('max-value', 'children'),
     Output('skew-value', 'children'),
     Output('range-value', 'children'),
     Output('data-table', 'data'),
     Output('histogram-graph', 'figure'),
     Output('gauge-graph', 'figure'),
     Output('stored-data', 'data'),
     Output('last-refresh-time', 'data'),
     Output('daily-report', 'children'),
     Output("refresh-toast", "is_open"),
     Output("footer-timestamp", "children"),
     Output("next-refresh-time", "data")],
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals'),
     Input('num-points-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('chart-type-radio', 'value'),
     Input('log-scale-switch', 'value')],
    [State('stored-data', 'data')]
)
def update_dashboard(n_clicks, n_intervals, num_points, start_date, end_date,
                     chart_type, log_scale_value,
                     stored_data):
    try:
        # Lecture du CSV sans en-tête
        expected_set = set(expected_columns)
        try:
            df = pd.read_csv('./data.csv')
            df.columns = [col.strip().lower() for col in df.columns]
            if not expected_set.issubset(set(df.columns)):
                raise Exception("En-tête absent")
        except Exception:
            df = pd.read_csv('./data.csv', header=None, names=expected_columns)
        
        df['time'] = pd.to_datetime(df['time'])
        df.sort_values('time', inplace=True)
        
        # Filtrage par dates
        df_filtered = filter_data_by_date(df, start_date, end_date)
        if num_points is not None and len(df_filtered) > num_points:
            df_filtered = df_filtered.tail(num_points)
        
        # Calcul des métriques sur "price"
        if not df_filtered.empty:
            last_val = df_filtered['price'].iloc[-1]
            mean_val = df_filtered['price'].mean()
            median_val = df_filtered['price'].median()
            std_val = df_filtered['price'].std()
            cv_val = (std_val / mean_val) * 100 if mean_val != 0 else 0
            skew_val = df_filtered['price'].skew()
            min_val = df_filtered['price'].min()
            max_val = df_filtered['price'].max()
            range_val = max_val - min_val
            # Pour la jauge, si au moins deux valeurs existent, on prend la valeur précédente comme référence.
            if len(df_filtered) > 1:
                prev_val = df_filtered['price'].iloc[-2]
            else:
                prev_val = last_val
        else:
            last_val = mean_val = median_val = std_val = cv_val = min_val = skew_val = max_val = range_val = 0
            prev_val = 0
        
        yaxis_type = "log" if "log" in log_scale_value else "linear"
        
        # --- Graphique principal avec dégradé (ligne) ou barres ---
        if chart_type == "line":
            x_values = df_filtered['time'].tolist()
            y_values = df_filtered['price'].tolist()
            
            y_base = min(y_values) if y_values else 0
            
            n_layers = 20
            gradient_traces = []
            for i in range(n_layers):
                frac_lower = i / n_layers
                frac_upper = (i + 1) / n_layers
                y_lower = [y_base + (val - y_base) * frac_lower for val in y_values]
                y_upper = [y_base + (val - y_base) * frac_upper for val in y_values]
                
                x_polygon = x_values + x_values[::-1]
                y_polygon = y_upper + y_lower[::-1]
                
                opacity_value = 0.2 * frac_upper
                gradient_traces.append(
                    go.Scatter(
                        x=x_polygon,
                        y=y_polygon,
                        fill='toself',
                        fillcolor=f'rgba(255,215,0,{opacity_value})',
                        mode='none',
                        line=dict(width=0),
                        hoverinfo='skip',
                        showlegend=False
                    )
                )
            
            trace_main = go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines',
                name='FTSE 100',
                line=dict(color=MAIN_COLOR, width=3),
                marker=dict(color=MAIN_COLOR, size=8)
            )
            data_live = gradient_traces + [trace_main]
        
        else:
            data_live = [go.Bar(
                x=df_filtered['time'],
                y=df_filtered['price'],
                marker=dict(color=MAIN_COLOR),
                name='FTSE 100'
            )]
        
        live_fig = go.Figure(data=data_live)
        live_fig.update_layout(
            title='Données du FTSE 100 en Temps Réel',
            xaxis=dict(title='Heure', color='#ffffff', tickformat='%H:%M:%S'),
            yaxis=dict(title='Prix', color='#ffffff', type=yaxis_type, autorange=True),
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            transition={'duration': 500}
        )
        
        # Histogramme des rendements
        if len(df_filtered) > 1:
            df_filtered['return'] = df_filtered['price'].pct_change() * 100
            returns = df_filtered['return'].dropna()
        else:
            returns = pd.Series([])
        
        hist_fig = go.Figure(
            data=go.Histogram(
                x=returns,
                marker=dict(color=MAIN_COLOR)
            )
        )
        hist_fig.update_layout(
            title='Distribution des Rendements',
            xaxis=dict(title='Rendement (%)', color='#ffffff'),
            yaxis=dict(title='Fréquence', color='#ffffff'),
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff')
        )
        
        # Gauge pour la dernière valeur avec comparaison au prix précédent
        gauge_min = min_val
        gauge_max = max_val
        if gauge_min == gauge_max:
            gauge_min -= 1
            gauge_max += 1
        
        gauge_fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=last_val,
                title={'text': "Dernière Valeur"},
                delta={'reference': prev_val},
                gauge={
                    'axis': {'range': [gauge_min, gauge_max]},
                    'bar': {'color': MAIN_COLOR},
                    'steps': [
                        {'range': [gauge_min, (gauge_min + gauge_max)/2], 'color': "#444"},
                        {'range': [(gauge_min + gauge_max)/2, gauge_max], 'color': "#666"}
                    ],
                    'threshold': {
                        'line': {'color': MAIN_COLOR, 'width': 4},
                        'thickness': 0.75,
                        'value': prev_val
                    }
                }
            )
        )
        gauge_fig.update_layout(
            template='plotly_dark',
            font=dict(color='#ffffff')
        )
        
        stored = df_filtered.to_dict('records')
        last_refresh = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_refresh_time = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        
        last_value_text = f"{last_val:.2f}"
        mean_value_text = f"{mean_val:.2f}"
        median_value_text = f"{median_val:.2f}"
        std_value_text = f"{std_val:.2f}"
        cv_value_text = f"{cv_val:.2f}%"
        min_value_text = f"{min_val:.2f}"
        max_value_text = f"{max_val:.2f}"
        range_value_text = f"{range_val:.2f}"
        skew_value_text = f"{skew_val:.2f}"
        
        daily_report_text = get_daily_report()
        footer_text = f"Dernière mise à jour : {last_refresh}"
        
        return (
            live_fig,
            last_value_text,
            mean_value_text,
            median_value_text,
            std_value_text,
            cv_value_text,
            min_value_text,
            max_value_text,
            skew_value_text,
            range_value_text,
            stored,
            hist_fig,
            gauge_fig,
            stored,
            last_refresh,
            daily_report_text,
            True,
            footer_text,
            next_refresh_time
        )
    except Exception as e:
        print("Erreur dans le callback:", e)
        return no_update

@app.callback(
    [Output("date-picker-range", "start_date"),
     Output("date-picker-range", "end_date")],
    [Input("clear-filter-button", "n_clicks")],
    prevent_initial_call=True,
)
def clear_filter(n_clicks):
    return ((datetime.datetime.now() - datetime.timedelta(days=1)).date(), datetime.datetime.now().date())

@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("download-csv", "n_clicks")],
    [State("stored-data", "data")],
    prevent_initial_call=True,
)
def download_csv(n_clicks, data):
    if data is None:
        return no_update
    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, "ftse_data.csv", index=False)

@app.callback(
    [Output("current-time", "children"),
     Output("countdown-text", "children"),
     Output("market-status", "children")],
    [Input("countdown-interval", "n_intervals")],
    [State("next-refresh-time", "data")]
)
def update_time_and_countdown(_, next_refresh):
    now = datetime.datetime.now()
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    market_status_div = get_market_status_div()
    
    if next_refresh is not None:
        try:
            next_refresh_dt = datetime.datetime.strptime(next_refresh, "%Y-%m-%d %H:%M:%S")
            delta = next_refresh_dt - now
            if delta.total_seconds() <= 0:
                countdown_str = "Actualisation imminente..."
            else:
                minutes, seconds = divmod(int(delta.total_seconds()), 60)
                countdown_str = f"Prochaine actualisation dans : {minutes} min {seconds} s"
        except ValueError:
            countdown_str = "Prochaine actualisation : indéterminée"
    else:
        countdown_str = "En attente de première actualisation..."
    
    return current_time_str, countdown_str, market_status_div

if __name__ == '__main__':
    app.run_server(debug=True)
