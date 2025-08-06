from validators.url import url as url_validator
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class UrlRepository:
    def __init__(self, db):
        self.db = db

    def find_by_id(self, url_id):
        result = self.db.execute(
            "SELECT * FROM urls WHERE id = %s", (url_id,)
        )
        return result[0] if result else None

    def find_by_name(self, name):
        result = self.db.execute(
            "SELECT * FROM urls WHERE name = %s", (name,)
        )
        return result[0] if result else None

    def get_url_checks(self, url_id):
        result = self.db.execute(
            "SELECT * FROM url_checks WHERE url_id = %s", (url_id,)
        )
        return result

    def get_urls_with_last_check(self):
        result = self.db.execute(
            '''
            SELECT DISTINCT ON (urls.id)
            urls.id,
            urls.name,
            url_checks.created_at,
            url_checks.status_code
            FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.id
                ORDER BY id DESC, url_checks.created_at DESC
            '''
        )
        return result

    def create_url(self, name):
        result = self.db.execute(
            "INSERT INTO urls (name) VALUES (%s) RETURNING id", (name, )
        )
        return result[0][0]

    def create_url_check(self, data):
        result = self.db.execute(
            '''
            INSERT INTO url_checks (url_id, status_code, title, h1, description) VALUES (%s, %s, %s, %s, %s)
            ''', (data['id'], data['status_code'], data['title'], data['h1'], data['description'])
        )
        return result


def url_validate(url):
    error_txt = None
    if url == "":
        error_txt = 'URL обязателен'
    elif len(url) > 255:
        error_txt = 'URL превышает 255 символов'
    elif url_validator(url) is not True:
        error_txt = 'Некорректный URL'
    return error_txt

def normalize_url(url):
    parsed = urlparse(url)
    first_part = f'{parsed.scheme}://'

    if parsed.port:
        second_part = f'{parsed.hostname}:{parsed.port}'
    else:
        second_part = f'{parsed.hostname}'

    url_string = f'{first_part}{second_part}'

    return url_string

def get_data(response_html):
    content = BeautifulSoup(response_html, 'html.parser')

    title = content.title.string if content.title else None
    h1 = content.h1.string if content.h1 else None
    description = content.find('meta', {'name': 'description'})
    description = description.get('content') if description else None
    return title, h1, description