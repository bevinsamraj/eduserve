import dash
from dash import dcc, html, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

from edusense.models.recommend import recommend_resources
from edusense.models.nlp_feedback import nlp_feedback

dash.register_page(__name__, path_template='/students/<student_id>', name='Students', icon='bi bi-people-fill')
dash.register_page(__name__, path='/students', name='Students', icon='bi bi-people-fill')


def layout(student_id=None, data=None):
    if data is None:
        return html.Div("Loading data...")

    df = pd.DataFrame(data)

    if student_id:
        # --- STUDENT PROFILE PAGE ---
        student_data = df[df['StudentID'] == student_id].iloc[0]
        # ... (Layout for individual student profile)
    else:
        # --- STUDENT ROSTER PAGE ---
        df['AvgScore'] = df[['Math', 'Science', 'English']].mean(axis=1).round(1)
        df['StudentLink'] = df.apply(lambda row: f"[{row['Student']}](/students/{row['StudentID']})", axis=1)

        return html.Div([
            # ... (Layout for student roster table)
        ])

# ... All callbacks for this page would go here ...