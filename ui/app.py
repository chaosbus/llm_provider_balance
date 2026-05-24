import threading
import time

import customtkinter as ctk
import requests

from config.manager import load_config
from providers import create_providers
from .model_dialog import ModelDialog
from .provider_card import ProviderCard
from .settings_dialog import SettingsDialog

REFRESH_MIN = 10      # minimum balance refresh interval (seconds)
MODEL_TTL = 300       # model cache TTL: 5 minutes


class App(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("LLM Provider Monitor")

        # Window — fixed size, exactly fits 3 providers
        self.geometry("560x340")
        self.resizable(False, False)

        # Config & providers
        self._config = load_config()
        self._providers = create_providers(self._config)
        self._refresh_timer: str | None = None
        self._model_timer: str | None = None

        # Model cache:  {key: (models, timestamp)}
        self._model_cache: dict[str, tuple[list[str], float]] = {}

        # ── Build UI ──
        self._build_toolbar()
        self._build_cards()
        self._build_statusbar()

        # ── Start lifecycle ──
        self._schedule_auto_refresh()
        self._schedule_model_auto_refresh()
        self.after(200, self.refresh_all)

    # ── UI Builders ──

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            toolbar,
            text="LLM Provider Monitor",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")

        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="⚙ 设置",
            width=68,
            height=30,
            command=self._open_settings,
        ).pack(side="left", padx=(4, 0))

        ctk.CTkButton(
            btn_frame,
            text="⟳ 刷新",
            width=68,
            height=30,
            command=self.refresh_all,
        ).pack(side="left", padx=(4, 0))

    def _build_cards(self):
        self._card_frame = ctk.CTkFrame(self)
        self._card_frame.pack(fill="both", expand=True, padx=14, pady=(4, 4))
        self._card_frame.grid_columnconfigure(0, weight=1)

        self._cards: dict[str, ProviderCard] = {}
        for prov in self._providers:
            key = prov.name.lower()
            card = ProviderCard(self._card_frame, prov.name)
            card.grid(row=len(self._cards), column=0, pady=(0, 6), sticky="ew")
            card.set_on_view_models(lambda k=key: self._view_models(k))
            self._cards[key] = card

    def _build_statusbar(self):
        interval = self._config.get("refresh_interval", 60)
        auto = self._config.get("auto_refresh", True)
        suffix = f"自动刷新 {interval}s" if auto else ""
        self._statusbar = ctk.CTkLabel(
            self,
            text=f"就绪    {suffix}",
            anchor="e",
            font=ctk.CTkFont(size=11),
            text_color=("#666666", "#999999"),
        )
        self._statusbar.pack(fill="x", padx=14, pady=(0, 6))

    # ── Refresh (balance + model cache) ──

    def refresh_all(self):
        """Refresh balances and pre-fetch model cache for all providers."""
        for prov in self._providers:
            self._refresh_balance(prov)
            if prov.configured:
                self._refresh_models(prov)

    def _refresh_balance(self, prov):
        key = prov.name.lower()
        card = self._cards[key]
        if not prov.configured:
            card.show_no_key()
            return
        card.show_loading()
        self._statusbar.configure(text=f"正在获取 {prov.name}...")
        threading.Thread(
            target=self._fetch_balance_task,
            args=(key, prov),
            daemon=True,
        ).start()

    def _fetch_balance_task(self, key: str, prov):
        try:
            data = prov.fetch_balance()
            self.after(0, lambda: self._on_balance_ok(key, data))
        except Exception as e:
            self.after(0, lambda: self._on_balance_err(key, e))

    def _on_balance_ok(self, key: str, data: dict):
        self._cards[key].display_balance(data)
        self._update_statusbar()

    def _on_balance_err(self, key: str, exc: Exception):
        self._cards[key].show_error(self._fmt_error(exc))
        self._statusbar.configure(text="就绪")

    # ── Model list (cached) ──

    def _refresh_models(self, prov):
        """Fetch models in background and store in cache."""
        threading.Thread(
            target=self._fetch_models_and_store,
            args=(prov,),
            daemon=True,
        ).start()

    def _fetch_models_and_store(self, prov):
        key = prov.name.lower()
        try:
            models = prov.fetch_models()
            self._model_cache[key] = (models, time.time())
        except Exception:
            pass  # model fetch failures are silent; balance errors are the signal

    def _view_models(self, key: str):
        prov = self._get_provider(key)
        if not prov or not prov.configured:
            return

        # Serve from cache if still fresh
        cached = self._model_cache.get(key)
        if cached and (time.time() - cached[1]) < MODEL_TTL:
            ModelDialog(self, prov.name, cached[0], parent_geometry=self.geometry())
            return

        # Cache miss → fetch and show
        self._cards[key].model_btn.configure(state="disabled", text="正在获取...")
        threading.Thread(
            target=self._fetch_models_show_task,
            args=(key, prov),
            daemon=True,
        ).start()

    def _fetch_models_show_task(self, key: str, prov):
        try:
            models = prov.fetch_models()
            self._model_cache[key] = (models, time.time())
            self.after(0, lambda: self._on_models_ok(key, prov.name, models))
        except Exception as e:
            self.after(0, lambda: self._on_models_err(key, e))

    def _on_models_ok(self, key: str, name: str, models: list[str]):
        self._cards[key].model_btn.configure(state="normal", text="📋 查看模型")
        ModelDialog(self, name, models, parent_geometry=self.geometry())

    def _on_models_err(self, key: str, exc: Exception):
        self._cards[key].model_btn.configure(state="normal", text="📋 查看模型")
        self._statusbar.configure(text=f"获取模型失败: {self._fmt_error(exc)}")

    # ── Balance auto-refresh timer (follows user setting) ──

    def _schedule_auto_refresh(self):
        if not self._config.get("auto_refresh", True):
            return
        interval = max(self._config.get("refresh_interval", 60), REFRESH_MIN) * 1000
        self._refresh_timer = self.after(interval, self._auto_tick)

    def _auto_tick(self):
        self.refresh_all()
        self._schedule_auto_refresh()

    # ── Model auto-refresh timer (fixed 5 minutes) ──

    def _schedule_model_auto_refresh(self):
        self._model_timer = self.after(MODEL_TTL * 1000, self._auto_model_tick)

    def _auto_model_tick(self):
        for prov in self._providers:
            if prov.configured:
                self._refresh_models(prov)
        self._schedule_model_auto_refresh()

    # ── Settings ──

    def _open_settings(self):
        dialog = SettingsDialog(self, self._config, parent_geometry=self.geometry())
        self.wait_window(dialog)
        if dialog.result is not None:
            self._config = load_config()
            self._providers = create_providers(self._config)
            self._model_cache.clear()
            if self._refresh_timer:
                self.after_cancel(self._refresh_timer)
                self._refresh_timer = None
            self._schedule_auto_refresh()
            self.refresh_all()
            self._update_statusbar()

    # ── Helpers ──

    def _get_provider(self, key: str):
        for p in self._providers:
            if p.name.lower() == key:
                return p
        return None

    def _update_statusbar(self):
        ts = time.strftime("%H:%M:%S")
        interval = self._config.get("refresh_interval", 60)
        auto = self._config.get("auto_refresh", True)
        suffix = f"自动刷新 {interval}s" if auto else ""
        self._statusbar.configure(text=f"上次刷新 {ts}    {suffix}")

    @staticmethod
    def _fmt_error(exc: Exception) -> str:
        if isinstance(exc, requests.exceptions.ConnectionError):
            return "网络连接失败"
        if isinstance(exc, requests.exceptions.Timeout):
            return "请求超时"
        if isinstance(exc, requests.exceptions.HTTPError):
            code = exc.response.status_code
            if code == 401:
                return "API Key 无效"
            if code == 429:
                return "请求过于频繁"
            return f"HTTP {code}"
        msg = str(exc)
        return msg if len(msg) < 60 else msg[:57] + "..."
