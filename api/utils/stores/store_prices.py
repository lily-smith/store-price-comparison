from .wegmans import Wegmans
from .aldi import Aldi
import json
from datetime import datetime

TAG_CACHE_MAX_AGE = 7 # in days
PRODUCT_CACHE_MAX_AGE = 7 # in days
STORE_ID_MAPPINGS = {0: 'aldi', 1: 'wegmans'}

product_cache = {0: {}, 1: {}}
product_tags_cache = {0: {}, 1: {}}

def is_cache_expired(cache_timestamp, max_age):
    cache_age = datetime.fromisoformat(cache_timestamp) - datetime.now()
    return cache_age.days >= max_age

def get_store_product_tags(store_id):
    if 'last_updated' in product_tags_cache[store_id]:
        cache_expired = is_cache_expired(
            product_tags_cache[store_id]['last_updated'], 
            TAG_CACHE_MAX_AGE
        )
        if not cache_expired:
            return product_tags_cache[store_id]

    with open('sample_product_info.json') as file:
        file_json = json.load(file)
        sample_product = file_json[STORE_ID_MAPPINGS[store_id]]
        print(sample_product)
        if store_id == 0:
            store = Aldi(sample_product['zip_code'], sample_product['city_name'])
        elif store_id == 1:
            store = Wegmans(sample_product['zip_code'], sample_product['city_name'])
        page_html = store.get_page_as_html(sample_product['name'])
        current_product_tags_cache = store.get_product_html_tags(page_html, sample_product['name'], sample_product['quantity'])
        product_tags_cache[store_id] = current_product_tags_cache
        product_tags_cache[store_id]['last_updated'] = datetime.now().isoformat()
    return product_tags_cache[store_id]

def get_prices_for_product(store_id, search_term, zip_code, city_name):
    key = f'{search_term},{zip_code},{city_name}'
    if key in product_cache[store_id]:
        cache_expired = is_cache_expired(
            product_cache[store_id][key]['last_updated'], 
            PRODUCT_CACHE_MAX_AGE
        )
        if not cache_expired:
            return product_cache[store_id][key]['product']
        
    if key in product_cache[store_id]:
        return product_cache[key]
    store = None
    if store_id == 0:
        store = Aldi(zip_code, city_name, get_store_product_tags(store_id))
    elif store_id == 1:
        store = Wegmans(zip_code, city_name, get_store_product_tags(store_id))
    if not store:
        return []
    print('search term:', search_term)
    products = store.get_products(search_term, headless=True)
    product_cache[store_id][key] = {
        'product': products[:min(10, len(products))],
        'last_updated': datetime.now().isoformat()
    }
    return product_cache[store_id][key]['product']
