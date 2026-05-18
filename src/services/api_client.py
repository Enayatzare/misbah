import json
from typing import Optional, Dict, Any
import urllib.parse

BASE_URL = "http://enayatzare98.ir/api"


class ApiClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.token: Optional[str] = None
        self.is_web = self._is_web_environment()

    def _is_web_environment(self) -> bool:
        try:
            import js
            return True
        except ImportError:
            return False

    def set_token(self, token: str):
        self.token = token

    def clear_token(self):
        self.token = None

    async def _web_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            from pyodide.http import pyfetch

            url = f"{self.base_url}/{endpoint}"
            request_data = {}
            if data:
                request_data.update(data)

            headers = {
                "Accept": "application/json",
            }

            # همه endpointها به جز auth (لاگین و ثبت‌نام) token می‌گیرند
            if self.token and "auth/" not in endpoint:
                url = f"{url}?token={self.token}"

            if method in ("GET", "PUT") and request_data:
                query_string = urllib.parse.urlencode(request_data)
                full_url = f"{url}&{query_string}" if "?" in url else f"{url}?{query_string}"
                response = await pyfetch(full_url, method=method, headers=headers)
            elif request_data:
                response = await pyfetch(
                    url,
                    method=method,
                    headers=headers,
                    body=json.dumps(request_data),
                )
            else:
                response = await pyfetch(url, method=method, headers=headers)

            if response.ok:
                try:
                    return await response.json()
                except:
                    return {"error": "پاسخ سرور معتبر نیست"}
            else:
                try:
                    error_data = await response.json()
                    return error_data
                except:
                    return {"error": f"Server error: {response.status}"}

        except Exception as e:
            print(f"Web request error ({method} {endpoint}):", e)
            return {"error": "خطا در ارتباط با سرور"}

    def _desktop_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            import requests

            url = f"{self.base_url}/{endpoint}"
            request_data = {}
            if data:
                request_data.update(data)

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            if self.token and "auth/" not in endpoint:
                request_data["token"] = self.token

            if method == "GET":
                response = requests.get(
                    url, params=request_data, headers=headers, timeout=30)
            else:
                response = requests.request(
                    method, url, json=request_data, headers=headers, timeout=30)

            try:
                return response.json()
            except:
                return {"error": "پاسخ سرور معتبر نیست"}

        except ImportError:
            return {"error": "کتابخانه requests نصب نیست"}
        except Exception as e:
            print(f"Desktop request error ({method} {endpoint}):", e)
            return {"error": "خطا در ارتباط با سرور"}

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        if self.is_web:
            import asyncio
            return asyncio.run(self._web_request("GET", endpoint, params))
        else:
            return self._desktop_request("GET", endpoint, params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        if self.is_web:
            import asyncio
            return asyncio.run(self._web_request("POST", endpoint, data))
        else:
            return self._desktop_request("POST", endpoint, data)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        if self.is_web:
            import asyncio
            return asyncio.run(self._web_request("PUT", endpoint, data))
        else:
            return self._desktop_request("PUT", endpoint, data)

    def delete(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        if self.is_web:
            import asyncio
            return asyncio.run(self._web_request("DELETE", endpoint, data))
        else:
            return self._desktop_request("DELETE", endpoint, data)


api = ApiClient()
