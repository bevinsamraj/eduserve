#feedback_engine.py

from transformers import pipeline
import pyttsx3

class FeedbackEngine:
    def __init__(self):
        try:
            self.feedback_gen = pipeline("text-generation", model="distilgpt2")
        except:
            self.feedback_gen = None
        self.tts_engine = pyttsx3.init()
    
    def generate_feedback(self, student_data):
        # Use ML, sentiment analysis, topic modeling, etc.
        prompt = f"Student {student_data['name']}, scores: {student_data['marks']}, remarks: {student_data['remarks']}"
        if self.feedback_gen:
            result = self.feedback_gen(prompt, max_length=40)[0]["generated_text"]
        else:
            result = "Needs more study in weak subjects."
        return result

    def speak_feedback(self, feedback_text):
        self.tts_engine.say(feedback_text)
        self.tts_engine.runAndWait()
