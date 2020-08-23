"""
This script is linking products from "Beliy Krolik"'s base with Yandex.Market.
Note: only products with article and brand name will be searched.
"""

from market_parser import MarketParser
import pandas as pd
import re
import time

# Global variables
PATH_TO_EXCEL = 'Goods_Brands.xlsx'

SEARCH_URL = 'https://market.yandex.ru/search?text='

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36', 'referer': 'https://www.google.com/'}

DEBUG = True


def has_cyrillic(s):
    """
    Function checks if string has cyrillic symbols.
    :param s: str
    :return: bool
            True if has, False otherwise.
    """
    return bool(re.search(r'[а-яА-ЯёЁ]', s))


def main():
    # Reading excel file
    df = pd.read_excel(PATH_TO_EXCEL)
    for index, row in df.iterrows():
        if index:
            product_article = row.get('Article')
            product_brand = row.get('BrandName')
            # Some articles are incorrect.
            # Obvious way to determine incorrect article is to check whether it has cyrillic symbols.
            # For example "КРАСНЫЙ" is incorrect.

            # Checking for cyrillic symbols.
            if not (MarketParser.__has_cyrillic__(product_article)):
                if DEBUG:
                    print("Searching for {}, {}".format(product_brand, product_article))
                result = MarketParser.search(product_article, product_brand, headers='auto', debug=True)
                print(result)
                time.sleep(3)
            else:
                if DEBUG:
                    print("Skipping {} assuming its wrong because it has cyrillic symbols".format(product_article))
        else:
            print("Skipped")


if __name__ == '__main__':
    main()
