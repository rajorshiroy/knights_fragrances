import requests
import config
from bs4 import BeautifulSoup
from pprint import pprint


class KnightsFragrances:
    def __init__(self):
        self.email = config.email
        self.password = config.password
        self.session = None
        self.categories = None

    def login(self):
        print('logging in...')
        # create the session
        self.session = requests.session()

        # set session headers
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/83.0.4103.116 Safari/537.36',
        }

        data = {
            'txtRegEmail': self.email,
            'txtPassword': self.password,
            'setAction': 'Login',
            'flFile': '',
            'flUrl': '',
            'txtSearch': '',
            'id': '',
        }

        # login
        response = self.session.post('https://www.knights-fragrances.co.uk/buying-wholesale-perfumes-login',
                                     data=data)
        if response.status_code == 200:
            print('logged in!')
        else:
            print('failed to log in.')
            quit()

    def get_categories(self):
        response = self.session.get('https://www.knights-fragrances.co.uk/womens-perfumes-wholesaler')
        soup = BeautifulSoup(response.content, 'html.parser')
        product_categories = soup.find('ul', {'class': 'ctgry_lst'}).find_all('li')
        self.categories = [{product_box.find('a')['title']: product_box.find('a')['href']} for product_box in
                           product_categories]
        print(f'{len(self.categories)} categories found')


if __name__ == '__main__':
    kf = KnightsFragrances()
    kf.login()
    kf.get_categories()
