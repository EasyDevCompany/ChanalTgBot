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


def get_urgent_information():
    url = ('https://32.mchs.gov.ru/deyatelnost/press-centr/'
           'operativnaya-informaciya')
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
    forecast_list = []
    try:
        response = requests.get(
            'https://api.openweathermap.org/data/2.5/forecast',
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
    holidays = []
    try:
        response = requests.get('https://my-calend.ru/holidays',
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
