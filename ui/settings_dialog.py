import customtkinter as ctk

from config.manager import save_config

REFRESH_OPTIONS = ["60", "120", "300", "600", "1800", "3600"]

PROVIDER_META = [
    ("kimi", "Kimi", "api.moonshot.cn"),
    ("deepseek", "DeepSeek", "api.deepseek.com"),
    ("siliconflow", "SiliconFlow", "api.siliconflow.cn"),
]


def _center_offset(parent_geo: str, w: int, h: int) -> tuple[int, int]:
    """Return (x, y) to center a w×h dialog on the parent window."""
    import re
    m = re.match(r"(\d+)x(\d+)[+]?([-]?\d+)[+]?([-]?\d+)", parent_geo)
    if not m:
        return (200, 200)
    pw, ph, px, py = int(m[1]), int(m[2]), int(m[3]), int(m[4])
    return (px + (pw - w) // 2, py + (ph - h) // 2)


class SettingsDialog(ctk.CTkToplevel):
    """Settings dialog for API keys and refresh interval."""

    W = 480
    H = 390

    def __init__(self, master, config: dict, parent_geometry: str = ""):
        super().__init__(master)
        self.title("设置")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Center on parent window
        x, y = _center_offset(parent_geometry, self.W, self.H)
        self.geometry(f"{self.W}x{self.H}+{x}+{y}")

        self.result: dict | None = None

        # ── API Keys section ──
        section_label = ctk.CTkLabel(
            self,
            text="Provider API Key",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        section_label.pack(anchor="w", padx=20, pady=(18, 8))

        keys_frame = ctk.CTkFrame(self)
        keys_frame.pack(fill="x", padx=20, pady=(0, 12))
        keys_frame.grid_columnconfigure(1, weight=1)

        self._entries = {}
        self._visible = {}

        for idx, (key, name, base_url) in enumerate(PROVIDER_META):
            # Label
            lbl = ctk.CTkLabel(
                keys_frame, text=name, anchor="w",
                font=ctk.CTkFont(size=13),
            )
            lbl.grid(row=idx, column=0, padx=(12, 8), pady=8, sticky="w")

            # Entry
            entry = ctk.CTkEntry(
                keys_frame,
                show="*",
                placeholder_text=f"{base_url} 的 API Key",
            )
            entry.insert(0, config.get("api_keys", {}).get(key, ""))
            entry.grid(row=idx, column=1, padx=(0, 4), pady=8, sticky="ew")
            self._entries[key] = entry

            # Toggle visibility button
            visible = ctk.CTkButton(
                keys_frame,
                text="👁",
                width=32,
                height=28,
                command=lambda k=key: self._toggle_visible(k),
            )
            visible.grid(row=idx, column=2, padx=(0, 12), pady=8)
            self._visible[key] = False

        # ── Refresh section ──
        refresh_label = ctk.CTkLabel(
            self,
            text="自动刷新",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        refresh_label.pack(anchor="w", padx=20, pady=(8, 8))

        refresh_frame = ctk.CTkFrame(self)
        refresh_frame.pack(fill="x", padx=20, pady=(0, 16))
        refresh_frame.grid_columnconfigure(1, weight=1)

        # Auto refresh toggle
        self._auto_var = ctk.BooleanVar(value=config.get("auto_refresh", True))
        auto_cb = ctk.CTkCheckBox(
            refresh_frame, text="启用自动刷新",
            variable=self._auto_var,
        )
        auto_cb.grid(row=0, column=0, padx=(12, 12), pady=(12, 4), sticky="w")

        # Interval
        interval_label = ctk.CTkLabel(
            refresh_frame, text="刷新周期（秒）:",
            font=ctk.CTkFont(size=13),
        )
        interval_label.grid(row=1, column=0, padx=(12, 8), pady=(4, 12), sticky="w")

        interval_var = ctk.StringVar(
            value=str(config.get("refresh_interval", 60))
        )
        interval_combo = ctk.CTkOptionMenu(
            refresh_frame,
            values=REFRESH_OPTIONS,
            variable=interval_var,
            width=100,
        )
        interval_combo.grid(row=1, column=1, padx=(0, 12), pady=(4, 12), sticky="w")
        self._interval_var = interval_var

        # ── Buttons ──
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(
            btn_frame, text="取消", width=80,
            fg_color=("#d1d5db", "#374151"),
            text_color=("#1a1a1a", "#e0e0e0"),
            hover_color=("#9ca3af", "#4b5563"),
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="保存", width=80,
            command=self._save,
        ).pack(side="right")

        self.bind("<Escape>", lambda e: self.destroy())

    # ── internals ──

    def _toggle_visible(self, key: str):
        self._visible[key] = not self._visible[key]
        self._entries[key].configure(show="" if self._visible[key] else "*")

    def _save(self):
        self.result = {
            "api_keys": {k: e.get() for k, e in self._entries.items()},
            "refresh_interval": int(self._interval_var.get()),
            "auto_refresh": self._auto_var.get(),
        }
        save_config(self.result)
        self.destroy()
