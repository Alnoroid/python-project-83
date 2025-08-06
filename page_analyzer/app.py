import os
import requests
from dotenv import load_dotenv
from flask import Flask,abort, render_template, request, flash, redirect, url_for
from page_analyzer.models.url import UrlRepository, url_validate, normalize_url, get_data
from page_analyzer.database import Database

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = Database(os.getenv('DATABASE_URL'))
url_repo = UrlRepository(db)

@app.get('/')
def root():
    return render_template('views/index.html')

@app.get('/urls')
def get_urls():
    urls = url_repo.get_urls_with_last_check()

    return render_template(
        'views/urls.html',
        urls=urls
    )

@app.get('/urls/<int:url_id>')
def get_url(url_id):
    url = url_repo.find_by_id(url_id)

    if not url:
        abort(404)

    url_checks = url_repo.get_url_checks(url_id)

    return render_template(
        'views/url.html',
        url=url,
        url_checks=url_checks
    )

@app.post('/urls')
def add_url():
    url = request.form.get('url')
    error_txt = url_validate(url)
    if error_txt is not None:
        flash(error_txt, 'danger')
        return render_template('views/index.html'), 422

    url_string = normalize_url(url)

    url_check = url_repo.find_by_name(url_string)
    if url_check is not None:
        flash('Страница уже существует', 'danger')
        return redirect(url_for('get_url', url_id=url_check[0]))
    try:
        new_url = url_repo.create_url(url_string)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_url', url_id=new_url))
    except Exception:
        flash('Ошибка при добавлении страницы', 'danger')
        return redirect(url_for('root'))


@app.post('/urls/<int:url_id>/checks')
def check_url(url_id):
    url = url_repo.find_by_id(url_id)
    try:
        response = requests.get(url[1])
        response.raise_for_status()
        code = response.status_code
        title, h1, description = get_data(response.text)
        data = {"id": url_id, "status_code": code, "title": title, "h1": h1, "description": description}
        url_repo.create_url_check(data)
        flash('Страница успешно проверена', 'success')
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
    return redirect(url_for('get_url', url_id=url_id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('views/404.html'), 404