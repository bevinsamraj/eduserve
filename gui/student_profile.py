#student_profile.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from ml.feedback_engine import FeedbackEngine

class StudentProfileWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.engine = FeedbackEngine()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Welcome, {user['email']} (Student)"))
        # Example: Load your data, show analytics, feedback, upload sections, etc.
        # feedback = self.engine.generate_feedback(student_data)
        # layout.addWidget(QLabel(feedback))
        self.setLayout(layout)
