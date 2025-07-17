import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

dash.register_page(__name__, path='/', name='Dashboard', icon='bi bi-speedometer2')

# Define layout within a function to accept data
def layout(data=None):
    if data is None:
        return html.Div("Loading data...")

    df = pd.DataFrame(data)
    df['AvgScore'] = df[['Math', 'Science', 'English']].mean(axis=1).round(1)

    # --- KPI Calculations ---
    total_students = len(df)
    class_avg_score = df['AvgScore'].mean()
    class_avg_attendance = df['Attendance'].mean()

    # --- Layout ---
    kpi_cards = dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader(html.I(className="bi bi-people-fill me-2") + "Total Students"), dbc.CardBody(f"{total_students}", className="fs-3 fw-bold")])),
        dbc.Col(dbc.Card([dbc.CardHeader(html.I(className="bi bi-star-fill me-2") + "Class Average Score"), dbc.CardBody(f"{class_avg_score:.1f}", className="fs-3 fw-bold")])),
        dbc.Col(dbc.Card([dbc.CardHeader(html.I(className="bi bi-check-circle-fill me-2") + "Average Attendance"), dbc.CardBody(f"{class_avg_attendance:.1f}%", className="fs-3 fw-bold")])),
    ])

    subject_avgs = df[['Math', 'Science', 'English']].mean().reset_index()
    subject_avgs.columns = ['Subject', 'Average Score']
    fig_subjects = px.bar(subject_avgs, x='Subject', y='Average Score', title='Class Average by Subject', text_auto='.1f', template='plotly_dark')

    fig_attendance = px.histogram(df, x='Attendance', title='Student Attendance Distribution', nbins=10, template='plotly_dark')

    main_charts = dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_subjects)), md=7),
        dbc.Col(dbc.Card(dcc.Graph(figure=fig_attendance)), md=5),
    ], className="mt-4")

    return html.Div([kpi_cards, main_charts])

# Callback to update the layout with data from the store
@callback(
    Output('page-content-dashboard', 'children'),
    Input('student-data-store', 'data')
)
def update_dashboard_layout(data):
    return layout(data)