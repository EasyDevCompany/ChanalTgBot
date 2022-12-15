import os
import httpx
import redis
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime
from dotenv import load_dotenv
import logging

logging.basicConfig(filename=f'{__name__}.log',
                    level=logging.INFO,
                    filemode='w',
                    encoding='UTF-8')


load_dotenv()

ua = UserAgent()

headers = {
    'user-agent': str(ua.chrome)
}

redis = redis.Redis('localhost', 6379, 0)


def get_urgent_information():
    url = os.getenv('MCHS')
    urgent_news = {}
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        today = int(datetime.datetime.now().strftime('%d'))
        things_list = soup.find_all('div', class_='articles-item')
        for thing in things_list:
            thing_date = thing.find('span', class_='articles-item__date').text
            if today - int(thing_date[:2]) <= 1:
                thing_title = thing.find('a',
                                         class_='articles-item__title').text
                thing_href = 'https://32.mchs.gov.ru' + thing.find(
                    'a', class_='articles-item__title').get('href')
                urgent_news[thing_title] = thing_href
                return urgent_news
    except Exception as e:
        logging.error('Нет ответа от сервера')
        logging.error(e)


def get_weather_today():
    url = os.getenv('WEATHER')
    forecast_list = []
    try:
        response = httpx.get(
            url,
            params={
                'id': 571476,
                'lang': 'ru',
                'units': 'metric',
                'APPID': os.getenv('WEATHER_API_KEY')
                }, headers=headers)
        result = response.json()
        today = int(datetime.datetime.now().strftime('%d'))
        for i in result['list']:
            if int(i['dt_txt'][8:10]) == today:
                forecast = (
                    i['dt_txt'] + '{0:+3.0f} '.format(i['main']['temp'])
                    + i['weather'][0]['description']
                    )
                forecast_list.append(forecast)
                return forecast_list
    except Exception as e:
        logging.error("Сайт недоступен")
        logging.error(e)


def get_weather_tomorrow():
    url = os.getenv('WEATHER')
    forecast_list = []
    try:
        response = httpx.get(
            url,
            params={
                'id': 571476,
                'lang': 'ru',
                'units': 'metric',
                'APPID': os.getenv('WEATHER_API_KEY')
                }, headers=headers)
        result = response.json()
        today = int(datetime.datetime.now().strftime('%d'))
        for i in result['list']:
            if int(i['dt_txt'][8:10]) - today == 1:
                forecast = (
                    i['dt_txt'] + '{0:+3.0f} '.format(i['main']['temp'])
                    + i['weather'][0]['description']
                    )
                forecast_list.append(forecast)
                return forecast_list
    except Exception as e:
        logging.error("Сайт недоступен")
        logging.error(e)


def get_horoscope():
    horoscope = {}
    signs = {
        'aries': 'Овен',
        'taurus': 'Телец',
        'gemini': 'Близнецы',
        'cancer': 'Рак',
        'leo': 'Лев',
        'virgo': 'Дева',
        'libra': 'Весы',
        'scorpio': 'Скорпион',
        'sagittarius': 'Стрелец',
        'capricorn': 'Козерог',
        'aquarius': 'Водолей',
        'pisces': 'Рыбы',
    }
    for sign in signs.items():
        try:
            response = httpx.get(
                f'https://horo.mail.ru/prediction/{sign[0]}/today/',
                headers=headers)
            result = response.text
            soup = BeautifulSoup(result, 'lxml')
            horoscope_text = soup.find(
                'div', class_=('article__item article__item_alignment_left '
                               'article__item_html')).text
            horoscope[sign[1]] = horoscope_text
        except Exception as e:
            horoscope['Exception horoscope'] = e
    return horoscope


def get_holidays():
    url = os.getenv('HOLY')
    holidays = []
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        holidays_list = soup.find('ul', class_='holidays-items').find_all('li')
        for holiday in holidays_list:
            holiday = holiday.text[:-5]
            holidays.append(holiday)
        return holidays
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_urgent_information_polling():
    url = os.getenv('MCHS')
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        thing_href = soup.find(
            'div', class_='articles-item').find(
                'a', class_='articles-item__title').get('href')
        response = httpx.get(f'https://32.mchs.gov.ru{thing_href}',
                             headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        text = soup.find('div', itemprop='articleBody').find_all('p', limit=3)
        message = ''
        for p in text:
            message += p.text
        image = soup.find('div', class_='public').find('img').get('src')
        image_url = 'https://32.mchs.gov.ru' + image
        if redis.get(message) is not None:
            if redis.get(message) != image_url.encode():
                redis.set(message, image_url, datetime.timedelta(days=2))
                return image_url, message
            else:
                return None
        else:
            logging.info(f'Ключа {message[:10]} не существует.')
            redis.set(message, image_url, datetime.timedelta(days=2))
            return image_url, message
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_info_from_newbryansk():
    url = os.getenv('NEWBR')
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        try:
            new_href = soup.find('section',
                                 class_='feed'
                                 ).find('div').find(
                                    'a', class_='post-title').get('href')
            new_href_url = 'https://newsbryansk.ru/' + new_href
            response = httpx.get(new_href_url, headers=headers)
            result = response.text
            soup = BeautifulSoup(result, 'lxml')
            title = soup.find('div',
                              class_='col-xs-12 page-container'
                              ).find('article').find('h1').text
            text = soup.find('div',
                             class_='col-xs-12 page-container'
                             ).find('article').find('div',
                                                    class_='post-content').text
            text = (text[:900] + '...') if len(text) > 900 else text
            image = soup.find('div',
                              class_='col-xs-12 page-container'
                              ).find('img').get('src')
            message = f'{title}{text}'
            if redis.get(message) is not None:
                if redis.get(message) != image.encode():
                    redis.set(message, image, datetime.timedelta(days=2))
                    return image, message
                else:
                    return None
            else:
                logging.info(f'Ключа {message[:10]} не существует.')
                redis.set(message, image, datetime.timedelta(days=2))
                return image, message
        except Exception:
            logging.info('Новости ещё не появились')
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_info_from_ria():
    url = os.getenv('RIA')
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        new_href = soup.find(
            'div', class_='list list-tags'
            ).find('div', class_='list-item'
                   ).find('div', class_='list-item__content'
                          ).find('a',
                                 class_=('list-item__title '
                                         'color-font-hover-only')
                                 ).get('href')
        response = httpx.get(new_href, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        title = soup.find('div', class_='article__title').text
        text = soup.find_all('div', class_='article__block', limit=2)
        message = f'{title}\n\n'
        for p in text:
            try:
                abzac = p.find('div', class_='article__text').text
                message += abzac + '\n\n'
            except Exception:
                abzac = p.find('div',
                               class_='article__quote-text m-small').text
                message += abzac
        image = soup.find('div', class_='media').find('img').get('src')
        if redis.get(image) is not None:
            if image.encode() not in redis.keys():
                redis.set(image, message, datetime.timedelta(days=2))
                return image, message
            else:
                return None
        else:
            logging.info(f'Ключа {image} не существует.')
            redis.set(image, message, datetime.timedelta(days=2))
            return image, message
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_info_from_bga():
    url = os.getenv('BGA')
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        new_title = soup.find(
            'div', class_='c9'
            ).find('div', class_='oneNewsBlock'
                   ).find('a').get('title')
        new_href = soup.find(
            'div', class_='c9'
            ).find('div', class_='oneNewsBlock'
                   ).find('a').get('href')
        image = soup.find(
            'div', class_='c9'
            ).find('div', class_='oneNewsBlock'
                   ).find('img').get('src')
        response = httpx.get(new_href, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        message = f'{new_title}\n\n'
        text = soup.find('div', class_='c9').find_all(['h2', 'p'], limit=5)
        for p in text:
            message += p.text
        if redis.get(message) is not None:
            if redis.get(message) != image.encode():
                redis.set(message, image, datetime.timedelta(days=2))
                return image, message
            else:
                return None
        else:
            logging.info(f'Ключа {message[:10]} не существует.')
            redis.set(message, image, datetime.timedelta(days=2))
            return image, message
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)


def get_info_from_bryanskobl():
    url = os.getenv('BO')
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        new_title = soup.find(
            'div', class_='grid_12'
            ).find('div', class_='grid_10 omega'
                   ).find('div', class_='news-header-item'
                          ).find('a').text
        new_href = soup.find(
            'div', class_='grid_12'
            ).find('div', class_='grid_10 omega'
                   ).find('div', class_='news-header-item'
                          ).find('a').get('href')
        try:
            image = soup.find(
                'div', class_='grid_12'
                ).find('div', class_='grid_2 alpha news-image-item'
                       ).find('img').get('src')
        except Exception:
            image = None
        new_href_url = 'http://www.bryanskobl.ru' + new_href
        response = httpx.get(new_href_url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        text = soup.find('div', class_='grid_12'
                         ).find('div',
                                class_='news-content').find_all('p', limit=3)
        message = f'{new_title}'
        for p in text:
            message += p.text
        if redis.get(message) is not None:
            if redis.get(message) != new_title.encode():
                redis.set(message, new_title, datetime.timedelta(days=2))
                return image, message
            else:
                return None
        else:
            logging.info(f'Ключа {message[:10]} не существует.')
            redis.set(message, new_title, datetime.timedelta(days=2))
            return image, message
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)
