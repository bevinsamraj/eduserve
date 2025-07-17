# app.py (for deployment)

from dash_app import create_dashboard
from flask import Flask

# Gunicorn looks for this 'server' variable
server = Flask(__name__) 
app = create_dashboard(server)

# The if __name__ == '__main__' block is not needed for deployment