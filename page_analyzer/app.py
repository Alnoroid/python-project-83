import os
from dotenv import load_dotenv
from flask import Flask, render_template


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
@app.route('/')
def root():
    return render_template('views/index.html')