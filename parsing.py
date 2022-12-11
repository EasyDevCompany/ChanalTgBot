import os
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime
from dotenv import load_dotenv

load_dotenv()

ua = UserAgent()

headers = {
    'user-agent': str(ua.chrome)
}

last_urgent = None
last_newbryansk = None
last_ria = None
last_bga = None
last_bo = None


def get_urgent_information():
    url = os.getenv('MCHS')
    urgent_news = {}
    try:
        response = requests.get(url, headers=headers)
        result = response.content
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
    except Exception as e:
        urgent_news['Exception (urgent news):'] = e
    return urgent_news


def get_weather():
    url = os.getenv('WEATHER')
    forecast_list = []
    try:
        response = requests.get(
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
    except Exception as e:
        forecast_list.append("Exception (forecast):", e)
    return forecast_list


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
            response = requests.get(
                f'https://horo.mail.ru/prediction/{sign[0]}/today/',
                headers=headers)
            result = response.content
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
        response = requests.get(url,
                                headers=headers)
        result = response.content
        soup = BeautifulSoup(result, 'lxml')
        holidays_list = soup.find('ul', class_='holidays-items').find_all('li')
        for holiday in holidays_list:
            holiday = holiday.text[:-5]
            holidays.append(holiday)
    except Exception as e:
        holidays.append(f'Error {e}')
    return holidays


def get_urgent_information_polling():
    url = os.getenv('MCHS')
    try:
        response = requests.get(url, headers=headers)
        result = response.content
        soup = BeautifulSoup(result, 'lxml')
        things_dict = {}
        thing = soup.find(
            'div', class_='articles-item').find(
                'a', class_='articles-item__title').text
        thing_href = soup.find(
            'div', class_='articles-item').find(
                'a', class_='articles-item__title').get('href')
        things_dict[thing] = 'https://32.mchs.gov.ru' + thing_href
    except Exception as e:
        things_dict['Error'] = f'Произошла ошибка - {e}'
    return things_dict


def check_update_urgent_information():
    global last_urgent
    data = get_urgent_information_polling()
    if last_urgent == data:
        return None
    else:
        last_urgent = data
        return last_urgent


def get_info_from_newbryansk():
    url = os.getenv('NEWBR')
    try:
        response = requests.get(url, headers=headers)
        result = response.content
        soup = BeautifulSoup(result, 'lxml')
        news_dict = {}
        new_title = soup.find('section',
                              class_='feed'
                              ).find('div').find('a', class_='post-title').text
        new_href = soup.find('section',
                             class_='feed'
                             ).find('div').find(
                                 'a', class_='post-title').get('href')
        news_dict[new_title] = url + new_href
    except Exception as e:
        news_dict['Error'] = f'Произошла ошибка - {e}'
    return news_dict


def check_update_newbryansk():
    global last_newbryansk
    data = get_info_from_newbryansk()
    if last_newbryansk == data:
        return None
    else:
        last_newbryansk = data
        return last_newbryansk


def get_info_from_ria():
    url = os.getenv('RIA')
    try:
        response = requests.get(url, headers=headers)
        result = response.content
        soup = BeautifulSoup(result, 'lxml')
        news_dict = {}
        new_title = soup.find(
            'div', class_='list list-tags'
            ).find('div', class_='list-item'
                   ).find('div', class_='list-item__content'
                          ).find('a',
                                 class_=('list-item__title '
                                         'color-font-hover-only')).text
        new_href = soup.find(
            'div', class_='list list-tags'
            ).find('div', class_='list-item'
                   ).find('div', class_='list-item__content'
                          ).find('a',
                                 class_=('list-item__title '
                                         'color-font-hover-only')).get('href')
        news_dict[new_title] = new_href
    except Exception as e:
        news_dict['Error'] = f'Произошла ошибка - {e}'
    return news_dict


def check_update_ria():
    global last_ria
    data = get_info_from_ria()
    if last_ria == data:
        return None
    else:
        last_ria = data
        return last_ria


def get_info_from_bga():
    url = os.getenv('BGA')
    try:
        response = requests.get(url, headers=headers)
        result = response.content
        soup = BeautifulSoup(result, 'lxml')
        news_dict = {}
        new_title = soup.find(
            'div', class_='c9'
            ).find('div', class_='oneNewsBlock'
                   ).find('a').get('title')
        new_href = soup.find(
            'div', class_='c9'
            ).find('div', class_='oneNewsBlock'
                   ).find('a').get('href')
        news_dict[new_title] = new_href
    except Exception as e:
        news_dict['Error'] = f'Произошла ошибка - {e}'
    return news_dict


def check_update_bga():
    global last_bga
    data = get_info_from_bga()
    if last_bga == data:
        return None
    else:
        last_bga = data
        return last_bga


def get_info_from_bryanskobl():
    url = os.getenv('BO')
    try:
        response = requests.get(url, headers=headers)
        result = response.content
        soup = BeautifulSoup(result, 'lxml')
        news_dict = {}
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
        news_dict[new_title] = 'http://www.bryanskobl.ru' + new_href
    except Exception as e:
        news_dict['Error'] = f'Произошла ошибка - {e}'
    return news_dict


def check_update_bo():
    global last_bo
    data = get_info_from_bryanskobl()
    if last_bo == data:
        return None
    else:
        last_bo = data
        return last_bo
