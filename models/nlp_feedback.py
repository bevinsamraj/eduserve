import pandas as pd
from textblob import TextBlob
import numpy as np

def nlp_feedback(row):
    """
    Generates a highly detailed, structured analysis of student performance,
    including a narrative summary, key metrics, strengths, and growth areas.
    """
    student_name = row['Student']
    subjects = ['Math', 'Science', 'English', 'History', 'Art']
    scores = {subject: row[subject] for subject in subjects}
    avg_score = np.mean(list(scores.values()))

    # --- Initialize Feedback Components ---
    strengths = []
    growth_areas = []
    
    # --- Detailed Analysis ---
    # 1. Overall Performance Tier
    if avg_score >= 90:
        performance_tier = "Excellent"
        summary_intro = f"{student_name} is demonstrating exceptional academic mastery across the board."
    elif avg_score >= 75:
        performance_tier = "Good"
        summary_intro = f"{student_name} maintains a strong and consistent performance."
    else:
        performance_tier = "Needs Improvement"
        summary_intro = f"While showing potential, {student_name} has several key areas for growth."

    # 2. Subject-Specific Analysis
    top_subject = max(scores, key=scores.get)
    top_score = scores[top_subject]
    weakest_subject = min(scores, key=scores.get)
    weakest_score = scores[weakest_subject]

    strengths.append({
        "icon": "bi bi-trophy-fill text-warning",
        "text": f"Top performance in {top_subject} with a score of {int(top_score)}."
    })

    if weakest_score < 70:
        growth_areas.append({
            "icon": "bi bi-tools text-danger",
            "text": f"The primary focus should be on {weakest_subject}, currently at {int(weakest_score)}."
        })

    # 3. Attendance Analysis
    attendance = row['Attendance']
    if attendance >= 95:
        attendance_status = "Excellent"
        strengths.append({
            "icon": "bi bi-calendar-check-fill text-success",
            "text": f"Exemplary attendance ({int(attendance)}%) shows strong commitment."
        })
    elif attendance < 80:
        attendance_status = "Needs Improvement"
        growth_areas.append({
            "icon": "bi bi-calendar-x-fill text-danger",
            "text": f"Improving attendance from {int(attendance)}% is a critical step for success."
        })
    else:
        attendance_status = "Good"

    # 4. Remarks Analysis
    remarks = str(row.get('Remarks', ''))
    if remarks:
        polarity = TextBlob(remarks).sentiment.polarity
        if polarity > 0.2:
            strengths.append({
                "icon": "bi bi-chat-heart-fill text-success",
                "text": "Teacher remarks note a positive attitude and active class engagement."
            })
        elif polarity < -0.1:
            growth_areas.append({
                "icon": "bi bi-chat-quote-fill text-warning",
                "text": "Remarks suggest some underlying challenges that could be addressed."
            })

    # --- Construct Narrative Summary ---
    summary_body = f"Their top subject is {top_subject}, where they excel. "
    if weakest_score < 70:
        summary_body += f"Conversely, the main area for development is {weakest_subject}. "
    summary_body += f"Attendance is currently rated as {attendance_status.lower()}."
    narrative_summary = summary_intro + " " + summary_body

    # --- Final Structured Feedback ---
    structured_feedback = {
        "summary": narrative_summary,
        "metrics": {
            "Performance Tier": performance_tier,
            "Top Subject": top_subject,
            "Area to Focus": weakest_subject if weakest_score < 70 else "None",
            "Attendance Status": attendance_status
        },
        "strengths": strengths,
        "growth_areas": growth_areas
    }
    
    # --- Maintain legacy return structure for compatibility ---
    legacy_feedback_text = narrative_summary
    text_analytics = {
        "polarity": TextBlob(remarks).sentiment.polarity if remarks else 0,
        "subjectivity": TextBlob(remarks).sentiment.subjectivity if remarks else 0,
    }
    
    return legacy_feedback_text, text_analytics, structured_feedback
