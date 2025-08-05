import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, make_response, redirect, url_for
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

    url_string = normalize_url(url)
    sql = f"INSERT INTO urls (name, created_at) VALUES ('{url_string}', '{datetime.today()}');"
    try:
        with conn.cursor() as curs:
            curs.execute(sql)
            conn.commit()
            flash('URL успешно добавлен', 'success')
            return redirect(url_for('root'), 302)
    except Exception as e:
        conn.rollback()
        flash(f'Ошибка при добавлении URL: {str(e)}', 'danger')
        return redirect(url_for('root'), 302)
        # return redirect(url_for('get_url', ), 302)

@app.get('/urls')
def get_urls():
    sql = ("SELECT urls.id, urls.name, MAX(url_checks.created_at) AS last_check_date FROM urls "
           "LEFT JOIN url_checks ON urls.id = url_checks.url_id GROUP BY urls.id"
           " ORDER BY urls.created_at DESC;")
    with conn.cursor() as curs:
        curs.execute(sql)
        urls = curs.fetchall()

    return render_template(
        'views/urls.html',
        urls=urls
    )

@app.get('/urls/<int:url_id>')
def get_url(url_id):
    sql = f"SELECT * FROM urls WHERE id = {url_id}"
    with conn.cursor() as curs:
        curs.execute(sql)
        url = curs.fetchone()

    sql = f"SELECT * FROM url_checks WHERE url_id = {url_id} ORDER BY created_at DESC;"
    with conn.cursor() as curs:
        curs.execute(sql)
        url_checks = curs.fetchall()

    if not url:
        return render_template('views/404.html'), 404

    return render_template(
        'views/url.html',
        url=url,
        url_checks=url_checks
    )

@app.post('/urls/<int:url_id>/checks')
def check_url(url_id):
    sql = f"INSERT INTO url_checks (url_id, created_at) VALUES ('{url_id}', '{datetime.today()}');"
    try:
        with conn.cursor() as curs:
            curs.execute(sql)
            conn.commit()
            flash('URL успешно проверен', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Ошибка при проверке URL: {str(e)}', 'danger')

    return redirect(url_for('get_url', url_id=url_id)), 302


if __name__ == '__main__':
    app.run()