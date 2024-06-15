from ..store import Store
import re
import time

class Aldi(Store):
    BASE_URL = 'https://shop.aldi.us/store/aldi/storefront/?current_zip_code={0}&utm_source=yext&utm_medium=local&utm_campaign=brand&utm_content=shopnow_storepage'
    URL = 'https://shop.aldi.us/store/aldi/s?k={0}'

    def __init__(self, zip_code, city_name):
        self.__zip_code = zip_code
        self.__city_name = city_name
        super(Aldi, self).__init__('Aldi', zip_code, city_name)
    
    def _set_store_location(self, page):
        page.goto(self.BASE_URL.format(self._zip_code))

    def _find_product_page(self, page, search_term):
        page.goto(self.URL.format(search_term))
        locator = page.get_by_text(re.compile('\$\d+.\d\d'))
        locator.nth(0).wait_for()
        
        for _ in range(10):
            page.keyboard.press('PageDown')
            time.sleep(0.1)

    def _get_product_name(self, product_html):
        name_div = product_html.find('h2', {'class': 'e-1s8iwuk'})
        if name_div:
            return name_div.text.strip()
        return ''

    def _get_product_price(self, product_html):
        price_div = product_html.find('div', {'class': 'e-k008qs'})
        if price_div:
            price = price_div.find('span', {'class': 'screen-reader-only'}).text.strip()
        else:
            price = 'Out of stock'
        return price
    
    def _get_product_quantity(self, product_html):
        quantity = product_html.find('div', {'class': 'e-isbvdh'})
        if not quantity:
            return ''
        return quantity.text.strip()
    
    def _get_product_image(self, product_html):
        images = product_html.find('img').get('srcset')
        image = images.split('https')[-1].split(' ')[0]
        return f'https{image}'
    
    def _get_product_availability(self, product_html):
        return self._get_product_price(product_html) != 'Out of stock'
    
    def _get_product_elements(self, soup):
        return soup.find_all('div', {'aria-label': 'Product'})

