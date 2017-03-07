import requests
from bs4 import BeautifulSoup

TIMEOUT = 20

def fetch_afisha_page(url):
    page = requests.get(url)
    return page.content


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html,'html.parser')
    movies_info = soup.find_all('div',{'class' : 'm-disp-table'})
    #add url
    movies_dict = [{
        'name' : movie.find('a').text,
        'url': movie.find('a').get('href'),
        'cinemas' : len(movie.parent.find_all('td',{'class' : 'b-td-item'}))
    } for movie in movies_info]
    return movies_dict

def get_movies_id(name):
    url = 'https://www.kinopoisk.ru/index.php?first=no&what=&kp_query='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }

    kinopois_info = requests.get(''.join([url,name]),headers = headers,timeout = TIMEOUT).content
    soup = BeautifulSoup(kinopois_info,'html.parser')
    try:
        parse = soup.find('a',text=name)
        id = parse['data-id']
        return id

    except (TypeError, KeyError):

        return None

def fetch_kinopoisk_html(movie_title):
    id = get_movies_id(movie_title)

    if id:
        url = 'https://www.kinopoisk.ru/film/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:45.0) Gecko/20100101 Firefox/42.0'
        }
        kinopois_info = requests.get(''.join([url, id]), headers=headers, timeout=TIMEOUT).content
        return kinopois_info
    else:
        return None

def fetch_movie_info(movies_title):

    kinopoisk_info = fetch_kinopoisk_html(movies_title)
    if kinopoisk_info:
        try:
            soup = BeautifulSoup(kinopoisk_info, 'html.parser')
            rating = soup.find('span',{'class' : 'rating_ball'}).text
            voters_number = soup.find('span',{'class' : 'ratingCount'}).text.replace(u'\xa0','')
        except AttributeError:
            return None,None

        if rating and voters_number:
            return rating, voters_number
    else :
        return None,None


def output_movies_to_console(movies):
    message = 'Фильм "{}" идет в {} кинотеатрах, имеет рейтинг {} и количество голосов {}'
    for movie in movies:
        print(message.format(
            movie['name'],
            movie['cinemas'],
            movie['rating'],
            movie['voters_number']
        ))


if __name__ == '__main__':
    print ('Получаем данные с afisha.ru.....')
    afisha_page = fetch_afisha_page('http://www.afisha.ru/msk/schedule_cinema/')
    afisha_list = parse_afisha_list(afisha_page)
    print (sorted(afisha_list, key= lambda movie: movie['cinemas'], reverse=True)[:10])
    print ('Получаем данные с kinopoisk.ru.....')

    for movie in afisha_list:
        rating, voters_number = fetch_movie_info(movie['name'])
        if rating and voters_number:
            movie.update({
                'rating' : rating ,
                'voters_number' : voters_number
            })
        else:
            movie.update({
                'rating': 0,
                'voters_number': 0
            })



    movies = sorted(afisha_list,key= lambda movie: float(movie['rating']) and movie['cinemas'], reverse=True)[:10]
    output_movies_to_console(movies)