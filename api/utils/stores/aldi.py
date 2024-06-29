from ..store import Store
import re
import time

class Aldi(Store):
    BASE_URL = 'https://new.aldi.us'
    URL = 'https://new.aldi.us/results?q={0}'

    def __init__(self, zip_code, city_name):
        self.__zip_code = zip_code
        self.__city_name = city_name
        super(Aldi, self).__init__('Aldi', zip_code, city_name)
    
    def _set_store_location(self, page):
        page.goto(self.BASE_URL)
        change_store_button = page.get_by_role('button', name=re.compile('\d{5}, \w+'))
        change_store_button.wait_for()
        change_store_button.click()

        continue_button = page.get_by_role('button', name='Continue')
        continue_button.wait_for()
        continue_button.click()

        zip_code_input = page.get_by_placeholder('ZIP code')
        zip_code_input.fill(self.__zip_code)
        zip_code_input.press('Enter')

        select_buttons = page.get_by_role('button', name='Select')
        select_buttons.wait_for()
        select_buttons.all()[0].click()

    def _find_product_page(self, page, search_term):
        page.goto(self.URL.format(search_term))
        locator = page.get_by_text(re.compile('\$\d+.\d\d'))
        locator.nth(0).wait_for()
        
        for _ in range(10):
            page.keyboard.press('PageDown')
            time.sleep(0.1)

    def _get_product_name(self, product_html):
        name_div = product_html.find('div', {'class': 'product-tile__name'})
        if name_div:
            return name_div.find('p').text.strip()
        return ''

    def _get_product_price(self, product_html):
        price_div = product_html.find('span', {'class': 'base-price__regular'})
        if price_div:
            price = price_div.text.strip()
        else:
            price = 'Out of stock'
        return price
    
    def _get_product_quantity(self, product_html):
        quantity = product_html.find('div', {'data-test': 'product-tile__product-detail'})
        if not quantity:
            return ''
        return quantity.text.strip()
    
    def _get_product_image(self, product_html):
        image = product_html.find('img').get('src')
        return image.replace('scaleWidth/153/', 'scaleWidth/306/')
    
    def _get_product_availability(self, product_html):
        return self._get_product_price(product_html) != 'Out of stock'
    
    def _get_product_elements(self, soup):
        return soup.find_all('div', {'class': 'product-tile'})

