from api.utils.store import Store
import re
import time
from bs4 import BeautifulSoup

class Aldi(Store):
    BASE_URL = 'https://new.aldi.us'
    URL = 'https://new.aldi.us/results?q={0}'
    STORES_URL = 'https://stores.aldi.us/'

    def __init__(self, zip_code, city_name, product_tags = {}):
        super(Aldi, self).__init__('Aldi', zip_code, city_name, product_tags)

    @classmethod
    def __get_store_location(self, page, store_url):
        page.goto(store_url)
        heading = page.get_by_role('heading')
        heading.nth(0).wait_for()
        soup = BeautifulSoup(page.content(), 'html.parser')
        store_heading = soup.find('h1', {'id': 'location-name'})
        store_address = soup.find_all('div', {'class': 'Address-line'})
        return (
            store_heading.text.replace('ALDI', '').strip(),
            store_address[0].text,
            store_address[1].text.split(',')[0],
            store_address[2].text
        )
    
    @classmethod
    def __get_subpage_links(self, page, subpage_url, label):
        page.goto(subpage_url)
        soup = BeautifulSoup(page.content(), 'html.parser')
        links = soup.find_all('a', {'class': 'Teaser-titleLink'})
        subpage_links = []
        for link in links:
            subpage_links.append({'label': label, 'href': link.get('href').replace('../', '')})
        return subpage_links

    @classmethod
    def __get_directory_links(self, page, directory_url):
        page.goto(directory_url)
        store_link = page.get_by_role('link')
        store_link.nth(10).wait_for()

        page_html = page.content()
        soup = BeautifulSoup(page_html, 'html.parser')
        directory_links = soup.find_all('a', {'class': 'Directory-listLink'})
        page_links = []
        for dir_link in directory_links:
            href = dir_link.get('href')
            if href.endswith(dir_link.text.lower().replace(' ', '-')):
                subpage_links = self.__get_subpage_links(page, self.STORES_URL + href, dir_link.text)
                page_links.extend(subpage_links)
            else:
                page_links.append({'label': dir_link.text, 'href': dir_link.get('href')})
        return page_links
    
    @classmethod
    def __get_state_store_locations(self, page, state_store_pages, state_abbr):
        state_store_locations = []
        for state_store_page in state_store_pages:
            store_url = self.STORES_URL + state_store_page['href']
            if state_store_page['href'].startswith('https'):
                store_url = state_store_page['href']
            store_name, street, city, zip_code = self.__get_store_location(page, store_url)
            state_store_locations.append({ 
                'url': store_url, 'state_abbr': state_abbr, 'name': store_name, 
                'street': street, 'city': city, 'zip_code': zip_code
            })
        return state_store_locations

    @classmethod
    def _get_store_locations(self, page):
        store_locations = []
        state_pages = self.__get_directory_links(page, self.STORES_URL)
        for state_page in state_pages:
            state_store_pages = self.__get_directory_links(page, self.STORES_URL + state_page['href'])
            state_store_locations = self.__get_state_store_locations(page, state_store_pages, state_page['href'].upper())
            store_locations.extend(state_store_locations)

        return store_locations
    
    def _set_store_location(self, page):
        page.goto(self.BASE_URL)
        acknowledge_button = page.get_by_role('button', name='Got it')
        if acknowledge_button:
            acknowledge_button.click()
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
            time.sleep(0.01)

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
    

