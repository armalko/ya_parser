"""
This library allows you to parse Yandex.Market. Uses of the functions are described in the implementations.
Author: Artem Malko.
"""

from lxml import html
import requests
import re
import fake_useragent


class MarketParser:
    @staticmethod
    def __get_headers(r, debug=False):
        """
        Function returns headers
        :param r: str
                  Set static if you don't want to use fake_useragent library
                  Otherwise set 'create'.
        :return: dict
                 Dict of headers ready-to-use
        """

        if r == 'static':
            return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36', 'referer': 'https://www.google.com/'}

        elif r == 'create':
            try:
                ua = fake_useragent.UserAgent()
                headers = {"User-Agent": ua.chrome, 'referer': 'https://www.google.com/'}

            except fake_useragent.errors.FakeUserAgentError:
                if debug:
                    print("Not being able to get a set of FakeUserAgent headers. Setting static instead.")
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
                           'referer': 'https://www.google.com/'}

            return headers

    @staticmethod
    def __has_cyrillic__(s):
        """
        Function checks if string has cyrillic symbols.
        :param s: str
        :return: bool
                True if has, False otherwise
        """

        return bool(re.search(r'[а-яА-ЯёЁ]', s))

    @staticmethod
    def search(article,
               brand,
               headers='static',
               proxies=False,
               debug=False,
               search_url='https://market.yandex.ru/search?text='):

        """
        Function to search products on Yandex.Market via article and brand name.

        :param article: str
        :param brand: str
        :param headers: str
                  Set 'static' if you don't want to use fake_useragent library
                  Otherwise set 'create'.
        :param proxies: bool
                  The use of proxies is in progress, but it is not yet complete.
        :param debug: bool
                  If you want to log function's activity, set True. Will be printed in terminal.
        :param search_url: str
        :return: str
                  link if product is found, None otherwise.
        """

        link = search_url + brand.replace(" ", "%") + '+' + article

        headers = MarketParser.__get_headers(headers, debug=debug)

        if proxies:
            # Check if proxies work correctly
            if requests.get("https://google.com", proxies=proxies).status_code == 200:
                response = requests.get(link, headers=headers)
            else:
                if debug:
                    print("Search Function:\n"
                          "Incorrect proxy address.\n")
                return None
        else:
            response = requests.get(link, headers=headers)

        if response.status_code != 200:
            if debug:
                print("Search Function logs: \n"
                      "Response status code is {}. Not being able to request.\n".format(response.status_code))
            return None

        # Using lxml tools to parse response.
        tree = html.fromstring(response.text)
        for el in tree.xpath('//@href'):
            # Every product link starts with '/product--'. Using this to find product's link
            if "/product--" in el:
                # Trimming the link. We don't need anything but product name and ID.
                # Every link looks like this:
                # /[product_name]/[id]?nid=[useless information]...
                # Finding the ?nid= and trimming.
                if debug:
                    print("Search Function logs: \n"
                          "Product found. Input parameters: article={}, brand={}\n".format(article, brand))
                return el[:el.find("?nid=")]

        # If no products are found returns None
        if debug:
            print("Search Function logs: \n"
                  "No product found. Input parameters: article={}, brand={}\n".format(article, brand))
            print(response.text)
        return None

    @staticmethod
    def get_prices(url,
                   headers='static',
                   proxies=False,
                   debug=False):
        """
        Function to get prices of product on Ya.Market via link.

        :param url: str
                    Link to the parsing product.
        :param headers: str
                  Set static if you don't want to use fake_useragent library
                  Otherwise set 'create'.
        :param proxies: bool
                  The use of proxies is in progress, but it is not yet complete.
        :param debug: bool
                  If you want to log function's activity, set True. Will be printed in terminal.
        :return: list
                  A list of prices. Soon will be added a list of ratings and names.
        """

        if proxies:
            pass

        headers = MarketParser.__get_headers(headers, debug=debug)
        page = requests.get(url,
                            headers=headers)

        # Formatting lxml tree to parse.
        tree = html.fromstring(page.text)
        elements = tree.xpath("//*[@data-autotest-currency='₽']")
        price_list = []
        for el in elements[1:]:
            price_list.append(el.xpath('span/text()')[0])

        if price_list:
            return price_list

        else:
            if debug:
                print("Get_Price function.\n"
                      "No prices found. URL_link = {}".format(url))
