from ..store import Store
import re
import time

class Wegmans(Store):
    BASE_URL = 'https://shop.wegmans.com'
    URL = 'https://shop.wegmans.com/search?search_term={0}&search_is_autocomplete=false'

    def __init__(self, zip_code, city_name, product_tags = {}):
        super(Wegmans, self).__init__('Wegmans', zip_code, city_name, product_tags)

    def _get_test_id_attribute(self):
        return 'data-test'
    
    def _set_store_location(self, page):
        page.goto(self.BASE_URL)
        outdated_button = page.get_by_text('I understand, proceed anyway.')
        if (outdated_button):
            outdated_button.click()

        close_modal = page.get_by_label('Modal close')
        close_modal.wait_for()
        close_modal.click()

        # close_modal = page.get_by_alt_text('Close the modal and return to the Wegmans app')
        # close_modal.wait_for()
        # close_modal.click()

        store_button = page.get_by_test_id('store-button')
        store_button.wait_for()
        store_button.click()

        zip_code_input = page.get_by_label('Enter City or Zip code')
        zip_code_input.wait_for()
        zip_code_input.fill(self._zip_code)
        zip_code_input.press('Enter')

        store_select = page.get_by_label(f'Select {self._city_name} Store')
        store_select.wait_for()
        store_select.click()

    def _find_product_page(self, page, search_term):
        page.goto(self.URL.format(search_term))
        # outdated_button = page.get_by_text('I understand, proceed anyway.')
        # if (outdated_button):
        #     outdated_button.click()
        locator = page.get_by_text(re.compile('\$\d+.\d\d.*'))
        locator.nth(0).wait_for()

        for _ in range(10):
            page.keyboard.press('PageDown')
            time.sleep(0.01)

    def _get_product_name(self, product_html):
        name_div = product_html.find(
            self._product_tags['name']['element'], 
            self._product_tags['name']['tags']
        )
        if name_div:
            return name_div.text.strip()
        return ''

    def _get_product_price(self, product_html):
        price_element = self._get_price_element(product_html)
        if not price_element:
            return ''
        return price_element.text.split()[0]
    
    def _get_product_quantity(self, product_html):
        quantity = product_html.find(
            self._product_tags['quantity']['element'], 
            self._product_tags['quantity']['tags']
        )
        if not quantity:
            return ''
        return quantity.get('title')
    
    def _get_product_image(self, product_html):
        return product_html.find('img').get('src')
    
    def _get_product_availability(self, product_html):
        out_of_stock = product_html.find('span', {'data-test': 'item-tile-out-of-stock'})
        return out_of_stock == None
    
    def _get_product_elements(self, soup):
        return soup.find_all('div', {'aria-label': 'Product'})
