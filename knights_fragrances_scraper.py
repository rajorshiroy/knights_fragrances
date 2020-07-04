import sys

import requests
import config
from bs4 import BeautifulSoup
from pprint import pprint
import string


class KnightsFragrances:
    PAGE_INDEXES = '1' + string.ascii_uppercase

    def __init__(self):
        self.email = config.email
        self.password = config.password
        self.session = None
        self.categories = []
        self.products = []

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
        for product_category in product_categories:
            category = product_category.find('a')
            title = category['title']
            title = title[:title.index('(')].strip()
            self.categories.append({
                'title': title,
                'url': category['href']
            })
        # pprint(self.categories)
        print(f'{len(self.categories)} categories found')

    def get_products_from_category(self, category):
        print(f'getting froducts from: {category["title"]}')
        response = self.session.get(category['url'])
        soup = BeautifulSoup(response.content, 'html.parser')
        if len(soup.find_all('div', {'class': 'pdct_tble'})) > 0:
            # when the category has product table
            for PAGE_INDEX in self.PAGE_INDEXES:
                url = f'{category["url"]}?prodGroup={PAGE_INDEX}'
                response = self.session.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                brand_boxes = soup.find_all('div', {'class': 'tbl_ctnt'})
                for brand_box in brand_boxes:
                    brand = brand_box.find('span', {'class': 'title_ctnt'}).text.strip()
                    products = brand_box.find_all('div', {'class': 'tblerw'})[1:]
                    for product in products:
                        self.products.append({
                            'category': category['title'],
                            'brand': brand,
                            'code': product.find('div', {'data-title': 'Product Code'}).text.strip(),
                            'name': product.find('div', {'data-title': 'Product Name'}).text.strip(),
                            'suggested_price': product.find('div', {'data-title': 'RRP* (£)'}).text.strip(),
                            'price': product.find('div', {'data-title': 'Price* (£)'}).text.strip(),
                        })
        else:
            # when the category does not have product table
            product_links = [pr['href'] for pr in soup.find_all('a', {'class': 'gft_wrap'})]
            product_count = len(product_links)
            for i, product_link in enumerate(product_links):
                response = self.session.get(product_link)
                soup = BeautifulSoup(response.content, 'html.parser')
                code = soup.find('span', {'class': 'rte_lbl'}, string='Code :').find_parent().text
                code = code[code.index(':') + 1:]
                self.products.append({
                    'category': category['title'],
                    'brand': '',
                    'code': code,
                    'name': soup.find('h1', {'class': 'hd_typ2'}).text.strip(),
                    'suggested_price': soup.find('span',
                                                 {'class': 'rte_lbl'},
                                                 string='Retail Price :').find_next_sibling().text,
                    'price': soup.find('span', {'class': 'rte_lbl'}, string='Cost :').find_next_sibling().text,
                })
                sys.stdout.write(f'\r{i + 1} out of {product_count} products scraped')
                sys.stdout.flush()
            sys.stdout.write('\r')
            sys.stdout.flush()

        pprint(self.products)
        print(f'{len(self.products)} products found')

    def test(self):
        res = self.session.get('https://www.knights-fragrances'
                               '.co.uk/4711-display-3-x-body-s'
                               'pray-100ml-3-x-cologne-stick-20'
                               'ml-3-x-watch-bottle-3-x-tissues'
                               '-2-x-cologne-100ml-spray')

        soup = BeautifulSoup(res.content, 'html.parser')
        code = soup.find('span', {'class': 'rte_lbl'}, string='Code :').find_parent().text
        code = code[code.index(':') + 1:]
        print(code)


if __name__ == '__main__':
    kf = KnightsFragrances()
    kf.login()
    kf.get_categories()
    kf.get_products_from_category(kf.categories[4])
