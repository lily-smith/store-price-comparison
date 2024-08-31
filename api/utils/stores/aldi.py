from ..store import Store
import re
import time

class Aldi(Store):
    BASE_URL = 'https://new.aldi.us'
    URL = 'https://new.aldi.us/results?q={0}'

    def __init__(self, zip_code, city_name, product_tags = {}):
        super(Aldi, self).__init__('Aldi', zip_code, city_name, product_tags)
    
    def _set_store_location(self, page):
        page.goto(self.BASE_URL)
        change_store_button = page.get_by_role('button', name=re.compile('\d{5}, \w+'))
        change_store_button.wait_for()
        change_store_button.click()

        continue_button = page.get_by_role('button', name='Continue')
        continue_button.wait_for()
        continue_button.click()

        zip_code_input = page.get_by_placeholder('ZIP code')
        zip_code_input.fill(self._zip_code)
        zip_code_input.press('Enter')

        select_buttons = page.get_by_role('button', name='Select')
        select_buttons.nth(0).wait_for()
        select_buttons.nth(0).click()

    def _find_product_page(self, page, search_term):
        page.goto(self.URL.format(search_term))
        locator = page.get_by_text(re.compile('\$\d+.\d\d'))
        locator.nth(0).wait_for()
        
        for _ in range(10):
            page.keyboard.press('PageDown')
            time.sleep(0.1)

    def _get_product_name(self, product_html):
        name_div = product_html.find(
            self._product_tags['name']['element'], 
            self._product_tags['name']['tags']
        )
        if not name_div:
            return ''
        return name_div.text.strip()

    def _get_product_price(self, product_html):
        price_div = self._get_price_element(product_html)
        if price_div:
            price = price_div.text.strip()
        else:
            price = 'Out of stock'
        return price
    
    def _get_product_quantity(self, product_html):
        quantity = product_html.find(
            self._product_tags['quantity']['element'], 
            self._product_tags['quantity']['tags']
        )
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

