from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from .wegmans import Wegmans
from .aldi import Aldi
import json
import re

stores = {
    'aldi': {
        'base_url': 'https://shop.aldi.us/store/aldi/storefront/?current_zip_code={0}&utm_source=yext&utm_medium=local&utm_campaign=brand&utm_content=shopnow_storepage',
        'url': 'https://shop.aldi.us/store/aldi/s?k={0}'
    }
}

def get_page_html(zip_code, store_city, search_term, store, headless=True):
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch() if headless \
            else p.chromium.launch(headless=False, slow_mo=2000)

        # Open a new browser page
        page = browser.new_page()

        # Set zip code
        page.goto(stores[store]['base_url'].format(zip_code))

        page.goto(stores[store]['url'].format(search_term))

        # Wait for prices to load
        locator = page.get_by_text(re.compile('\$\d+.\d\d'))
        locator.nth(0).wait_for()
        page_content = page.content()

        soup = BeautifulSoup(page_content, 'html.parser')
        # with open('temp.html', 'w') as file:
        #     file.write(soup.prettify())

        # Close browser
        browser.close()
        return soup


def get_aldi_products(zip_code, store_city, search_term, headless=True):
    soup = get_page_html(zip_code, store_city, search_term, 'aldi', headless)

    products = soup.find_all('div', {'aria-label': 'Product'})
    result = []
    for product in products:
        name = product.find('span', {'class': 'e-8zabzc'}).text.strip()
        if not re.match(f'.*{search_term}.*', name.lower()):
            continue
        #print(name)
        price_div = product.find('div', {'class': 'e-k008qs'})
        if price_div:
            price = price_div.find('span', {'class': 'screen-reader-only'}).text.strip()
        else:
            price = 'Out of stock'
        quantity = product.find('div', {'class': 'e-1wczau3'}).text.strip()
        images = product.find('img').get('srcset')
        image = images.split('https')[-1].split(' ')[0]
        result.append((name, price, quantity, f'https{image}'))
    return result

# wegmans = Wegmans('Wegmans', '02155', 'Medford')
# products = wegmans.get_products('eggs', headless=False)
# for i in range(10):
#     print(products[i])
#     print()

# aldi = Aldi('Aldi', '02155', 'Medford')
# products = aldi.get_products('eggs', headless=True)
# for i in range(min(10, len(products))):
#     print(products[i])
#     print()

def get_prices_for_product():
    aldi = Aldi('02155', 'Medford', get_product_tags('aldi'))
    products = aldi.get_products('eggs', headless=True)
    return products[:min(10, len(products))]

def get_product_tags(store):
    with open('sample_product_info.json') as file:
        file_json = json.load(file)
        sample_product = file_json[store]
        if store == 'aldi':
            store = Aldi(sample_product['zip_code'], sample_product['city_name'])
        if store == 'wegmans':
            store = Wegmans(sample_product['zip_code'], sample_product['city_name'])
        print(sample_product)
        page_html = store.get_page_as_html(sample_product['name'])  
        return store.get_product_html_tags(page_html, sample_product['name'], sample_product['quantity'])

print(get_prices_for_product())