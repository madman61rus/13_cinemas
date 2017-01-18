import requests
from bs4 import BeautifulSoup

TIMEOUT = 20

def fetch_afisha_page(url):
    page = requests.get(url)
    return page.content


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html,'html.parser')
    movies_info = soup.find_all('div',{'class' : 'm-disp-table'})
    movies_dict = [{
        'name' : movie.find('a').text,
        'count' : len(movie.parent.find_all('td',{'class' : 'b-td-item'}))
    } for movie in movies_info]
    return movies_dict

def get_movies_id(name):
    url = 'https://www.kinopoisk.ru/index.php?first=no&what=&kp_query='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }

    kinopois_info = requests.get(''.join([url,name]),headers = headers,timeout = TIMEOUT).content
    soup = BeautifulSoup(kinopois_info,'html.parser')
    parse = soup.find('a',text=name)
    if parse:
        id = parse['data-id']
        return id
    else:
        return None


def fetch_movie_info(movie_title):

    id = get_movies_id(movie_title)

    if id:
        url = 'https://www.kinopoisk.ru/film/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        }

        kinopois_info = requests.get(''.join([url,id]), headers=headers, timeout=TIMEOUT).content
        soup = BeautifulSoup(kinopois_info, 'html.parser')
        rating = soup.find('span',{'class' : 'rating_ball'}).text
        rating_count = soup.find('span',{'class' : 'ratingCount'}).text.replace(u'\xa0','')

        return rating, rating_count


def output_movies_to_console(movies):
    message = 'Фильм "{}" идет в {} кинотеатрах, имеет рейтинг {} и количество голосов {}'
    for movie in movies:
        print(message.format(
            movie['name'],
            movie['count'],
            movie['rating'],
            movie['rating_count']
        ))


if __name__ == '__main__':
    print ('Получаем данные с afisha.ru.....')
    afisha_page = fetch_afisha_page('http://www.afisha.ru/msk/schedule_cinema/')
    afisha_list = parse_afisha_list(afisha_page)

    print ('Получаем данные с kinopoisk.ru.....')

    for counter,movie in enumerate(afisha_list,start=1):
        try:
            rating, rating_count = fetch_movie_info(movie['name'])
            print('Фильм номер {}. Получаем данные rating- {}, rating_count {}'.format(counter,rating,rating_count))
            movie.update({
                'rating' : rating ,
                'rating_count' : rating_count
            })
        except (TypeError,AttributeError):
            print ('Не могу получить данные с сайта')
            movie.update({
                'rating': 0,
                'rating_count': 0
            })



    movies = sorted(afisha_list,key= lambda movie: float(movie['rating']) and movie['count'], reverse=True)[:9]
    output_movies_to_console(movies)