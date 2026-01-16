import requests
import json
import httpx
from bot.utils.constants import API_URL, BOT_API_TOKEN

class APIClient:

    def __init__(self, user_id: int | None = None):
        self.base_url = API_URL
        self.headers = {
            "X-BOT-TOKEN": BOT_API_TOKEN,
            "X-USER-ID": str(user_id)
        }
        self.client = httpx.AsyncClient(timeout=30)

    # -----------------------------
    #           API-request
    # -----------------------------
    async def _request(self, method: str, endpoint: str, data=None, files=None):
        url = f"{self.base_url}{endpoint}"

        try:
            response = await self.client.request(method=method, url=url, data=data, files=files, headers=self.headers)

            if response.status_code >= 400:
                try:
                    error = response.json()
                    return {
                        "success": False,
                        "statusCode": response.status_code,
                        "message": error.get("message", "Ошибка API"),
                        "response": error
                    }
                except ValueError:
                    return {
                        "success": False,
                        "statusCode": response.status_code,
                        "message": f"HTTP ошибка {response.status_code}",
                        "response": {}
                    }

            return response.json()

        except httpx.HTTPError as e:
            return {
                "success": False,
                "statusCode": 500,
                "message": f"Ошибка сети: {e}",
                "response": {}
            }


    # -----------------------------
    #          Методы API
    # -----------------------------
    async def check_user(self):
        return await self._request("GET", "/bot/check-user")

    async def get_categories(self):
        return await self._request("GET", "/categories")

    async def add_category(self, data, files=None):
        return await self._request("POST", "/categories", data=data, files=files)

    async def update_category(self, cat_id, data, files=None):
        return await self._request("PUT", f"/categories/{cat_id}", data=data, files=files)

    async def delete_category(self, cat_id):
        return await self._request("DELETE", f"/categories/{cat_id}")

    async def get_products(self):
        return await self._request("GET", "/products")

    async def add_product(self, data, files=None):
        return await self._request("POST", "/products", data=data, files=files)

    async def update_product(self, prod_id, data, files=None):
        return await self._request("PUT", f"/products/{prod_id}", data=data, files=files)

    async def delete_product(self, prod_id):
        return await self._request("DELETE", f"/products/{prod_id}")
