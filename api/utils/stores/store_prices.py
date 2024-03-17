from .wegmans import Wegmans
from .aldi import Aldi

def get_prices_for_product(store_id, search_term, zip_code, city_name):
  store = None
  if store_id == 0:
    store = Aldi(zip_code, city_name)
  elif store_id == 1:
    store = Wegmans(zip_code, city_name)
  if not store:
    return []
  print('search term:', search_term)
  products = store.get_products(search_term, headless=True)
  return products[:min(10, len(products))]
