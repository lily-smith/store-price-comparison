from flask import Flask, request, jsonify, Response
from .utils.stores.store_prices import get_prices_for_product

app = Flask(__name__)

@app.route('/api/prices/<int:store_id>', methods=['GET'])
def get_prices(store_id):
    args = request.args
    if ('search_term' not in args or 'zip_code' not in args or 'city_name' not in args):
        return Response('Missing values for search_term, zip_code, and/or city_name', status=400)

    return jsonify(
        get_prices_for_product(
            store_id, 
            args['search_term'], 
            args['zip_code'], args['city_name']
        )
    )

if __name__ == '__main__':
    app.run(debug=True)