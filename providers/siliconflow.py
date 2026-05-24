from .base import BaseProvider


class SiliconFlowProvider(BaseProvider):
    name = "SiliconFlow"
    base_url = "https://api.siliconflow.cn"

    def fetch_balance(self) -> dict:
        resp = self._session.get(f"{self.base_url}/v1/user/info", timeout=10)
        resp.raise_for_status()
        data = resp.json()["data"]
        total = float(data["totalBalance"])
        charge = float(data["chargeBalance"])
        balance = float(data["balance"])
        return {
            "primary": f"¥{total:.2f}",
            "items": [
                ("总余额", f"¥{total:.2f}"),
                ("充值余额", f"¥{charge:.2f}"),
                ("赠送余额", f"¥{balance:.2f}"),
            ],
        }

    def fetch_models(self) -> list[str]:
        resp = self._session.get(f"{self.base_url}/v1/models", timeout=10)
        resp.raise_for_status()
        return [m["id"] for m in resp.json()["data"]]
