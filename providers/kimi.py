from .base import BaseProvider


class KimiProvider(BaseProvider):
    name = "Kimi"
    base_url = "https://api.moonshot.cn"

    def fetch_balance(self) -> dict:
        resp = self._session.get(f"{self.base_url}/v1/users/me/balance", timeout=10)
        resp.raise_for_status()
        data = resp.json()["data"]
        return {
            "primary": f"¥{data['available_balance']:.2f}",
            "items": [
                ("可用余额", f"¥{data['available_balance']:.2f}"),
                ("现金余额", f"¥{data['cash_balance']:.2f}"),
                ("代金券", f"¥{data['voucher_balance']:.2f}"),
            ],
        }

    def fetch_models(self) -> list[str]:
        resp = self._session.get(f"{self.base_url}/v1/models", timeout=10)
        resp.raise_for_status()
        return [m["id"] for m in resp.json()["data"]]
