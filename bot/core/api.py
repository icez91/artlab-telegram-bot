import requests
import json
from bot.utils.constants import API_URL

class APIClient:
    def get_categories(self):
        try:
            r = requests.get(f"{API_URL}/categories")
            return r.json()
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def add_category(self, data, files=None):
        try:
            r = requests.post(f"{API_URL}/categories", data=data, files=files)
            return r.json()
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def update_category(self, cat_id, data, files=None):
        try:
            r = requests.put(f"{API_URL}/categories/{cat_id}", data=data, files=files)
            return r.json()
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def delete_category(self, cat_id):
        try:
            r = requests.delete(f"{API_URL}/categories/{cat_id}")
            return r.json()
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def get_products(self):
        try:
            r = requests.get(f"{API_URL}/products")
            return r.json()
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def add_product(self, data, files=None):
        try:
            r = requests.post(f"{API_URL}/products", data=data, files=files)
            return r.json()
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def update_product(self, prod_id, data, files=None):
        try:
            r = requests.put(f"{API_URL}/products/{prod_id}", data=data, files=files)
            return r.json()
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def delete_product(self, prod_id):
        try:
            r = requests.delete(f"{API_URL}/products/{prod_id}")
            return r.json()
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}
