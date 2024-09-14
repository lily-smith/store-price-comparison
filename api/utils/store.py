from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright
import re
from bs4 import BeautifulSoup

class Store(ABC):
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/69.0.3497.100 Safari/537.36"
    )

    def __init__(self, name, zip_code, city_name, product_tags):
        self._name = name
        self._zip_code = zip_code
        self._city_name = city_name
        self._product_tags = product_tags

    def _get_test_id_attribute(self):
        return None

    @abstractmethod
    def _set_store_location(self, page):
        ...

    @abstractmethod
    def _find_product_page(self, page, search_term):
        ...

    def get_page_as_html(self, search_term, headless=True):
        with sync_playwright() as playwright:
            test_id_attribute = self._get_test_id_attribute()
            if test_id_attribute:
                playwright.selectors.set_test_id_attribute(test_id_attribute)
            browser = playwright.chromium.launch() if headless \
                else playwright.chromium.launch(headless=False, slow_mo=2000)
            page = browser.new_page(user_agent=self.USER_AGENT)
            self._set_store_location(page)
            self._find_product_page(page, search_term)
            return page.content()
    
    def __clean_attrs(self, attrs):
        attrs.pop('title', None)
        
    def get_product_html_tags(self, page_html, product_name, quantity):
        soup = BeautifulSoup(page_html, 'html.parser')
        name_element = soup.find(lambda tag: tag.name and tag.text == product_name)
        self.__clean_attrs(name_element.attrs)
        quantity_element = soup.find(lambda tag: tag.name and tag.text == quantity)
        self.__clean_attrs(quantity_element.attrs)
        return {
            'name': {'element': name_element.name, 'tags': name_element.attrs}, 
            'quantity': {'element': quantity_element.name, 'tags': quantity_element.attrs}
        }
    
    def _get_price_element(self, product_html):
        return product_html.find(lambda tag: tag.name and re.match(r'\$\d+\.\d{2}', tag.text))
        
    @abstractmethod
    def _get_product_name(self, product_html):
        ...

    @abstractmethod       
    def _get_product_price(self, product_html):
        ...

    @abstractmethod       
    def _get_product_quantity(self, product_html):
        ...
    
    @abstractmethod       
    def _get_product_availability(self, product_html):
        ...

    @abstractmethod       
    def _get_product_image(self, product_html):
        ...

    @abstractmethod
    def _get_product_elements(self, soup):
        ...

    def __get_product_info(self, product_html):
        return {
            'name': self._get_product_name(product_html),
            'price': self._get_product_price(product_html),
            'quantity': self._get_product_quantity(product_html),
            'is_in_stock': self._get_product_availability(product_html),
            'image_url': self._get_product_image(product_html)
        }

    def get_products(self, search_term, headless=True):
        page_html = self.get_page_as_html(search_term, headless)
        soup = BeautifulSoup(page_html, 'html.parser')
        product_elements = self._get_product_elements(soup)
        products = []
        for product_html in product_elements:
            name = self._get_product_name(product_html)
            if not re.match(f'.*{search_term}.*', name.lower()):
                continue
            products.append(self.__get_product_info(product_html))
        return products
        
    

    
    
