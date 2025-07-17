import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback, dash_table

import dash_bootstrap_components as dbc

# Import functions from model files
from models.nlp_feedback import nlp_feedback
from models.recommend import recommend_resources

# --- Constants ---
DATA_PATH = "data/students.csv"
DEFAULT_THEME = dbc.themes.CYBORG
SUBJECTS = ['Math', 'Science', 'English', 'History', 'Art']

# --- Helper Functions ---
def load_data():
    """Load student data from CSV, handle missing file and columns."""
    try:
        df = pd.read_csv(DATA_PATH)
        all_cols = ['StudentID', 'Student'] + SUBJECTS + ['Attendance', 'Remarks', 'PhotoURL']
        for col in all_cols:
            if col not in df.columns:
                df[col] = '' if col in ['Remarks', 'PhotoURL', 'Student', 'StudentID'] else 0
        
        df['Remarks'] = df['Remarks'].fillna('')
        df['PhotoURL'] = df['PhotoURL'].fillna('')
        df.fillna(0, inplace=True)

        df[SUBJECTS + ['Attendance']] = df[SUBJECTS + ['Attendance']].astype(float)
        df['StudentID'] = df['StudentID'].astype(str)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['StudentID', 'Student'] + SUBJECTS + ['Attendance', 'Remarks', 'PhotoURL'])
    return df

def save_data(df):
    """Save DataFrame to CSV."""
    df.to_csv(DATA_PATH, index=False)
    
# --- Main App Creation ---
def create_dashboard(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname="/",
        external_stylesheets=[DEFAULT_THEME, dbc.icons.BOOTSTRAP],
        suppress_callback_exceptions=True,
    )

    # --- App Layout ---
    app.layout = dbc.Container([
        dcc.Store(id='student-data-store', data=load_data().to_dict('records')),
        dbc.NavbarSimple(brand="EduSense AI Dashboard", color="primary", dark=True, className="mb-4"),
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ], fluid=True, className="dbc")
    
    # --- Page Layout Functions ---
    def main_dashboard_layout():
        return html.Div([
            dbc.Row(id='kpi-cards-row', className="mb-4"),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(id='subject-avg-chart')), md=7),
                dbc.Col(dbc.Card(dcc.Graph(id='performance-dist-chart')), md=5),
            ], className="mb-4"),
            dbc.Card([
                dbc.CardHeader(dbc.Row([
                    dbc.Col(html.H4("Student Roster"), width="auto"),
                    dbc.Col(dbc.Button("＋ Add New Student", href="/entry", color="success"), width="auto")
                ], justify="between", align="center")),
                dbc.CardBody(
                    dash_table.DataTable(
                        id='student-roster-table',
                        columns=[
                            {'name': 'ID', 'id': 'StudentID'},
                            {'name': 'Student Name', 'id': 'StudentLink', 'type': 'text', 'presentation': 'markdown'},
                            {'name': 'Avg. Score', 'id': 'AvgScore'},
                            {'name': 'Attendance %', 'id': 'Attendance'},
                            {'name': 'Actions', 'id': 'Actions', 'type': 'text', 'presentation': 'markdown'}
                        ],
                        style_cell={'textAlign': 'left', 'backgroundColor': '#222', 'color': 'white', 'border': '1px solid #444'},
                        style_header={'fontWeight': 'bold', 'backgroundColor': '#333', 'border': '1px solid #444'},
                        markdown_options={"html": True}, page_size=10,
                    )
                )
            ])
        ])
    
    def data_entry_page(student_id=None):
        page_title = "Add New Student"
        button_label = "Save Student"
        
        initial_values = {col: '' for col in ['id', 'name', 'remarks', 'photo']}
        initial_values.update({s.lower(): None for s in SUBJECTS})
        initial_values['attendance'] = None

        if student_id:
            df = pd.DataFrame(load_data())
            student_data = df[df['StudentID'] == student_id].iloc[0]
            initial_values = {
                'id': student_data['StudentID'], 'name': student_data['Student'],
                'attendance': student_data['Attendance'], 'remarks': student_data['Remarks'], 'photo': student_data['PhotoURL']
            }
            for s in SUBJECTS:
                initial_values[s.lower()] = student_data[s]
            page_title = f"Editing: {student_data['Student']}"
            button_label = "Update Student"

        return html.Div([
            dbc.Button([html.I(className="bi bi-arrow-left"), " Back to Dashboard"], href="/", className="mb-3"),
            html.H2(page_title),
            dbc.Card(dbc.CardBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([dbc.Label("Student ID"), dbc.Input(id="entry-student-id", value=initial_values['id'], type="text", disabled=bool(student_id))], md=6),
                        dbc.Col([dbc.Label("Student Full Name"), dbc.Input(id="entry-student-name", value=initial_values['name'], type="text")], md=6)
                    ], className="mb-3"),
                    html.Hr(),
                    dbc.Label("Subject Marks (out of 100)"),
                    dbc.Row(
                        [dbc.Col([dbc.Label(s), dbc.Input(id=f"entry-{s.lower()}-score", value=initial_values[s.lower()], type="number")]) for s in SUBJECTS],
                        className="mb-3"
                    ),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([dbc.Label("Attendance (%)"), dbc.Input(id="entry-attendance", value=initial_values['attendance'], type="number")], md=6),
                        dbc.Col([dbc.Label("Photo URL"), dbc.Input(id="entry-photo-url", value=initial_values['photo'], type="text")], md=6)
                    ], className="mb-3"),
                    dbc.Label("Teacher's Remarks"),
                    dbc.Textarea(id="entry-remarks", value=initial_values['remarks'], placeholder="Add remarks here...", rows=4, className="mb-3"),
                    dbc.Button(button_label, id="save-entry-button", color="primary", className="mt-3")
                ])
            ]))
        ])

    def student_profile_layout(student_id):
        df = pd.DataFrame(load_data())
        student_data = df[df['StudentID'] == student_id].iloc[0]
        
        scores = student_data[SUBJECTS]
        avg_score = scores.mean()
        weakest_subject = scores.idxmin() if scores.sum() > 0 else "N/A"
        best_subject = scores.idxmax() if scores.sum() > 0 else "N/A"
        recommendations = recommend_resources(weakest_subject) if weakest_subject != "N/A" else None
        _, _, structured_feedback = nlp_feedback(student_data)
        
        photo_url = student_data['PhotoURL'] if pd.notna(student_data['PhotoURL']) and student_data['PhotoURL'] else 'https://placehold.co/150x150/2a3a49/6c757d?text=No+Image'

        def create_metric_card(title, value, icon):
            return dbc.Card([
                dbc.CardBody([
                    html.H6(title, className="card-title text-muted"),
                    html.H4(value, className="card-text"),
                    html.I(className=f"{icon} position-absolute top-0 end-0 p-3 fs-2 text-muted")
                ])
            ], className="position-relative")

        def create_feedback_list(points, color):
            if not points:
                return dbc.Alert("None to display.", color="secondary")
            return [
                dbc.ListGroupItem([
                    html.I(className=f"{point['icon']} me-3 fs-5 text-{color}"),
                    point['text']
                ], className="d-flex align-items-center border-0 bg-transparent") for point in points
            ]

        # --- Create Radar Chart ---
        radar_fig = go.Figure()
        radar_fig.add_trace(go.Scatterpolar(
            r=list(scores.values) + [scores.values[0]], # Add first value to end to close the shape
            theta=list(scores.index) + [scores.index[0]], # Add first label to end
            fill='toself',
            name='Scores'
        ))
        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title="Skills Profile"
        )

        return html.Div([
            dbc.Row([
                 dbc.Col(dbc.Button([html.I(className="bi bi-arrow-left"), " Back to Dashboard"], href="/"), width="auto"),
                 dbc.Col(dbc.Button("Edit This Student", href=f"/entry/{student_id}", color="secondary"), width="auto")
            ], justify="between", className="mb-3"),
            
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Img(src=photo_url, className="img-fluid rounded-circle", style={'maxWidth': '150px', 'maxHeight': '150px', 'objectFit': 'cover'}), width="auto"),
                        dbc.Col([
                            html.H2(student_data['Student']),
                            html.H5(f"ID: {student_data['StudentID']}", className="text-muted")
                        ], align="center")
                    ])
                ])
            ], className="mb-4"),

            dbc.Tabs([
                dbc.Tab(label="Performance Overview", children=[
                    dbc.Row([
                        dbc.Col(create_metric_card("Average Score", f"{avg_score:.1f}", "bi bi-calculator"), md=3),
                        dbc.Col(create_metric_card("Attendance", f"{student_data['Attendance']:.0f}%", "bi bi-calendar-check"), md=3),
                        dbc.Col(create_metric_card("Best Subject", best_subject, "bi bi-trophy"), md=3),
                        dbc.Col(create_metric_card("Weakest Subject", weakest_subject, "bi bi-tools"), md=3),
                    ], className="mt-4"),
                    dbc.Row([
                        dbc.Col(dbc.Card(dcc.Graph(figure=radar_fig)), md=5, className="mt-4"),
                        dbc.Col(dbc.Card([
                            dbc.CardHeader("Score Breakdown"),
                            dbc.CardBody(dcc.Graph(
                                figure=px.bar(x=scores.index, y=scores.values, labels={'x': 'Subject', 'y': 'Score'}, text=scores.values, template="plotly_dark")
                                    .update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                            ))
                        ]), md=7, className="mt-4"),
                    ])
                ]),
                dbc.Tab(label="AI Feedback Analysis", children=[
                    dbc.Card(dbc.CardBody([
                        html.H4("AI Narrative Summary"),
                        html.P(structured_feedback['summary'], className="lead"),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                html.H5("Key Strengths"),
                                dbc.ListGroup(create_feedback_list(structured_feedback['strengths'], 'success'), flush=True)
                            ], md=6),
                            dbc.Col([
                                html.H5("Growth Opportunities"),
                                dbc.ListGroup(create_feedback_list(structured_feedback['growth_areas'], 'danger'), flush=True)
                            ], md=6)
                        ])
                    ]), className="mt-3")
                ]),
                dbc.Tab(label="Learning Resources", children=[
                     dbc.Card(dbc.CardBody([
                        html.H4(f"Recommended Resources for {weakest_subject}", className="mb-4"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([html.I(className="bi bi-globe me-2"), "Helpful Websites"]),
                                    dbc.ListGroup([
                                        dbc.ListGroupItem([
                                            html.A(site['name'], href=site['url'], target="_blank", className="fw-bold"),
                                            html.P(site['description'], className="mb-0 text-muted small")
                                        ]) for site in recommendations.get('websites', [])
                                    ], flush=True)
                                ], className="h-100")
                            ], md=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([html.I(className="bi bi-book me-2"), "Suggested Reading"]),
                                    dbc.ListGroup([
                                        dbc.ListGroupItem([
                                            html.Div(item['name'], className="fw-bold"),
                                            html.P(item['description'], className="mb-0 text-muted small")
                                        ]) for item in recommendations.get('reading', [])
                                    ], flush=True)
                                ], className="h-100")
                            ], md=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader([html.I(className="bi bi-youtube me-2"), "Instructional Videos"]),
                                    dbc.CardBody([
                                        *[html.Div([
                                            html.H6(video['name']),
                                            html.Iframe(
                                                src=video['embed_url'],
                                                width="100%",
                                                height="200",
                                                style={'border': 'none', 'borderRadius': '5px'}
                                            )
                                        ], className="mb-3") for video in recommendations.get('videos', [])]
                                    ])
                                ], className="h-100")
                            ], md=4),
                        ])
                    ]), className="mt-3") if recommendations else dbc.Alert("No specific recommendations available.", color="info", className="mt-3")
                ]),
            ])
        ])

    # --- Callbacks ---
    @app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
    def display_page(pathname):
        if pathname == '/entry': return data_entry_page()
        if pathname and pathname.startswith('/entry/'): return data_entry_page(student_id=pathname.split('/')[-1])
        if pathname and pathname.startswith('/profile/'): return student_profile_layout(student_id=pathname.split('/')[-1])
        return main_dashboard_layout()

    @app.callback(
        Output('kpi-cards-row', 'children'),
        Output('subject-avg-chart', 'figure'),
        Output('performance-dist-chart', 'figure'),
        Output('student-roster-table', 'data'),
        Input('student-data-store', 'data')
    )
    def update_dashboard(data):
        if not data: return [], {}, {}, []
        
        df = pd.DataFrame(data)
        df['AvgScore'] = df[SUBJECTS].mean(axis=1).round(1)

        kpi_cards = dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader([html.I(className="bi bi-people-fill me-2"), "Total Students"]), dbc.CardBody(f"{len(df)}", className="fs-3 fw-bold")])),
            dbc.Col(dbc.Card([dbc.CardHeader([html.I(className="bi bi-star-fill me-2"), "Class Average Score"]), dbc.CardBody(f"{df['AvgScore'].mean():.1f}", className="fs-3 fw-bold")])),
            dbc.Col(dbc.Card([dbc.CardHeader([html.I(className="bi bi-check-circle-fill me-2"), "Average Attendance"]), dbc.CardBody(f"{df['Attendance'].mean():.1f}%", className="fs-3 fw-bold")])),
        ])
        
        subject_avgs = df[SUBJECTS].mean().reset_index()
        subject_avgs.columns = ['Subject', 'Average Score']
        fig_subjects = px.bar(subject_avgs, x='Subject', y='Average Score', title='Class Average by Subject', text_auto='.1f', template='plotly_dark')
        fig_subjects.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        bins = [0, 60, 70, 80, 90, 101]
        labels = ['Poor (<60)', 'Needs Improvement (60-69)', 'Average (70-79)', 'Good (80-89)', 'Excellent (90+)']
        df['Performance Tier'] = pd.cut(df['AvgScore'], right=False, bins=bins, labels=labels)
        tier_counts = df['Performance Tier'].value_counts(sort=False).reset_index()
        fig_performance = px.pie(tier_counts, values='count', names='Performance Tier', title='Class Performance Distribution', hole=0.4, template='plotly_dark')
        fig_performance.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        df['StudentLink'] = df.apply(lambda row: f"[{row['Student']}](/profile/{row['StudentID']})", axis=1)
        df['Actions'] = df.apply(lambda row: f'<a href="/entry/{row["StudentID"]}" class="btn btn-sm btn-outline-secondary ms-1">Edit</a>', axis=1)
        table_data = df.to_dict('records')

        return kpi_cards, fig_subjects, fig_performance, table_data

    @app.callback(
        Output('url', 'pathname'),
        Output('student-data-store', 'data'),
        Input('save-entry-button', 'n_clicks'),
        [State('url', 'pathname'), State('student-data-store', 'data'),
         State('entry-student-id', 'value'), State('entry-student-name', 'value')]
        + [State(f'entry-{s.lower()}-score', 'value') for s in SUBJECTS]
        + [State('entry-attendance', 'value'), State('entry-remarks', 'value'), State('entry-photo-url', 'value')],
        prevent_initial_call=True
    )
    def save_student_data(n_clicks, pathname, data, student_id, name, *args):
        df = pd.DataFrame(data)
        
        form_values = list(args)
        scores = form_values[:len(SUBJECTS)]
        attendance, remarks, photo_url = form_values[len(SUBJECTS):]

        new_data = {'StudentID': student_id, 'Student': name, 'Attendance': float(attendance or 0), 'Remarks': remarks, 'PhotoURL': photo_url}
        for i, subject in enumerate(SUBJECTS):
            new_data[subject] = float(scores[i] or 0)

        if pathname == '/entry':
            if student_id in df['StudentID'].values: return '/entry', data
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        else:
            edit_student_id = pathname.split('/')[-1]
            idx = df[df['StudentID'] == edit_student_id].index[0]
            for key, value in new_data.items():
                df.loc[idx, key] = value

        save_data(df)
        return '/', df.to_dict('records')

    return app