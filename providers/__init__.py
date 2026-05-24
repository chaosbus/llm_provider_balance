from .kimi import KimiProvider
from .deepseek import DeepSeekProvider
from .siliconflow import SiliconFlowProvider

PROVIDER_CLASSES = {
    "kimi": KimiProvider,
    "deepseek": DeepSeekProvider,
    "siliconflow": SiliconFlowProvider,
}


def create_providers(config: dict) -> list:
    """Create provider instances from config dict."""
    api_keys = config.get("api_keys", {})
    return [cls(api_keys.get(key, "")) for key, cls in PROVIDER_CLASSES.items()]
