from validators.url import url as url_validator
from urllib.parse import urlparse

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