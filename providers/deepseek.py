from .base import BaseProvider


class DeepSeekProvider(BaseProvider):
    name = "DeepSeek"
    base_url = "https://api.deepseek.com"

    def fetch_balance(self) -> dict:
        resp = self._session.get(f"{self.base_url}/user/balance", timeout=10)
        resp.raise_for_status()
        info = resp.json()["balance_infos"][0]
        total = float(info["total_balance"])
        topped = float(info["topped_up_balance"])
        granted = float(info["granted_balance"])
        return {
            "primary": f"¥{total:.2f}",
            "items": [
                ("总余额", f"¥{total:.2f}"),
                ("充值余额", f"¥{topped:.2f}"),
                ("赠金余额", f"¥{granted:.2f}"),
            ],
        }

    def fetch_models(self) -> list[str]:
        resp = self._session.get(f"{self.base_url}/models", timeout=10)
        resp.raise_for_status()
        return [m["id"] for m in resp.json()["data"]]
