import customtkinter as ctk


class ProviderCard(ctk.CTkFrame):
    """Compact card widget — title+button on same row, balance horizontal."""

    def __init__(self, master, provider_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.provider_name = provider_name
        self.grid_columnconfigure(1, weight=1)

        # Row 0 — title | model button
        self.header = ctk.CTkLabel(
            self,
            text=provider_name,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.header.grid(row=0, column=0, padx=(14, 0), pady=(8, 0), sticky="w")

        self.model_btn = ctk.CTkButton(self, text="📋 查看模型", height=24, width=90)
        self.model_btn.grid(row=0, column=2, padx=(0, 14), pady=(8, 0), sticky="e")

        # Row 1 — accent line
        self.accent = ctk.CTkFrame(self, height=1, fg_color=("#2563eb", "#3b82f6"))
        self.accent.grid(row=1, column=0, columnspan=3, pady=(4, 6), padx=14, sticky="ew")

        # Row 2 — content (primary + detail items, horizontal flow)
        self._content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._content_frame.grid(row=2, column=0, columnspan=3, padx=14, pady=(0, 8), sticky="ew")
        # col 0 = primary, col 1 = detail separator, col 2 = detail items
        self._content_frame.grid_columnconfigure(2, weight=1)

        self.primary_label = ctk.CTkLabel(
            self._content_frame,
            text="",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.primary_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self._detail_labels: list[ctk.CTkLabel] = []

        # initial state
        self.show_loading()

    # ── public API ──

    def set_on_view_models(self, callback):
        self.model_btn.configure(command=callback)

    def display_balance(self, data: dict):
        self.primary_label.configure(text=data["primary"])
        self._clear_detail()
        for label, value in data["items"]:
            lbl = ctk.CTkLabel(
                self._content_frame,
                text=f"{label} {value}",
                font=ctk.CTkFont(size=12),
                text_color=("#4b5563", "#9ca3af"),
            )
            lbl.grid(row=0, column=len(self._detail_labels) + 2, padx=(0, 14), sticky="w")
            self._detail_labels.append(lbl)

    def show_loading(self):
        self.primary_label.configure(text="")
        self._clear_detail()
        lbl = ctk.CTkLabel(
            self._content_frame,
            text="正在获取...",
            font=ctk.CTkFont(size=12),
        )
        lbl.grid(row=0, column=2, sticky="w")
        self._detail_labels.append(lbl)

    def show_error(self, message: str):
        self.primary_label.configure(text="⚠")
        self._clear_detail()
        lbl = ctk.CTkLabel(
            self._content_frame,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color="#e74c3c",
        )
        lbl.grid(row=0, column=2, sticky="w")
        self._detail_labels.append(lbl)

    def show_no_key(self):
        self.primary_label.configure(text="--")
        self._clear_detail()
        lbl = ctk.CTkLabel(
            self._content_frame,
            text="请先配置 API Key",
            font=ctk.CTkFont(size=12),
            text_color=("#888888", "#999999"),
        )
        lbl.grid(row=0, column=2, sticky="w")
        self._detail_labels.append(lbl)

    # ── helpers ──

    def _clear_detail(self):
        for w in self._detail_labels:
            w.destroy()
        self._detail_labels.clear()
