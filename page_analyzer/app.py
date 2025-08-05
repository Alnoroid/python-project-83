import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, make_response, redirect, url_for, get_flashed_messages
from page_analyzer.models.url import url_validate, normalize_url

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

@app.get('/')
def root():
    return render_template('views/index.html')



@app.post('/urls')
def add_urls():
    url = request.form.get('url')
    error_txt = url_validate(url)
    if error_txt is not None:
        flash(error_txt, 'danger')
        return redirect(url_for('root'), 302)
    else:
        url_string = normalize_url(url)
        sql = f"INSERT INTO urls (name, created_at) VALUES ('{url_string}', '{datetime.today()}');"
        try:
            with conn.cursor() as curs:
                curs.execute(sql)
                conn.commit()
                flash('URL успешно добавлен', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Ошибка при добавлении URL: {str(e)}', 'danger')
            return redirect(url_for('root'), 302)

        return redirect(url_for('root'), 302)

@app.get('/urls')
def get_urls():
    sql = "SELECT * FROM urls ORDER BY created_at DESC;"
    with conn.cursor() as curs:
        curs.execute(sql)
        urls = curs.fetchall()

    return render_template(
        'views/urls.html',
        urls=urls
    )

@app.get('/urls/<int:id>')
def get_url(id):
    sql = f"SELECT * FROM urls WHERE id = {id}"
    with conn.cursor() as curs:
        curs.execute(sql)
        url = curs.fetchone()

    if not url:
        flash('Страницы не существует', 'danger')
        return redirect(url_for('root'), 302)

    return render_template(
        'views/url.html',
        url=url
    )
