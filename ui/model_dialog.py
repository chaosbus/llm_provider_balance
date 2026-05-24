import customtkinter as ctk


def _center_offset(parent_geo: str, w: int, h: int) -> tuple[int, int]:
    """Return (x, y) to center a w×h dialog on the parent window."""
    import re
    m = re.match(r"(\d+)x(\d+)[+]?([-]?\d+)[+]?([-]?\d+)", parent_geo)
    if not m:
        return (200, 200)
    pw, ph, px, py = int(m[1]), int(m[2]), int(m[3]), int(m[4])
    return (px + (pw - w) // 2, py + (ph - h) // 2)


class ModelDialog(ctk.CTkToplevel):
    """Searchable model list dialog. Click a model name to copy it."""

    W = 420
    H = 340

    def __init__(self, master, provider_name: str, models: list[str], parent_geometry: str = ""):
        super().__init__(master)
        self.title(f"{provider_name} - 模型列表")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Center on parent window
        x, y = _center_offset(parent_geometry, self.W, self.H)
        self.geometry(f"{self.W}x{self.H}+{x}+{y}")

        self._models = models
        self._filtered = models[:]

        # ── Search row (entry + clear button) ──
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(fill="x", padx=16, pady=(16, 10))
        search_row.grid_columnconfigure(0, weight=1)

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", self._on_search)
        self._search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="输入关键词搜索模型...",
            textvariable=self._search_var,
        )
        self._search_entry.grid(row=0, column=0, sticky="ew")
        self._search_entry.focus_set()

        self._clear_btn = ctk.CTkButton(
            search_row, text="✕", width=30, height=28,
            command=self._clear_search,
        )
        self._clear_btn.grid(row=0, column=1, padx=(4, 0))

        # ── Model count ──
        self._count_label = ctk.CTkLabel(
            self,
            text=f"共 {len(models)} 个模型",
            font=ctk.CTkFont(size=11),
            text_color=("#666666", "#999999"),
        )
        self._count_label.pack(anchor="w", padx=16, pady=(0, 6))

        # ── Scrollable list ──
        self._list_frame = ctk.CTkScrollableFrame(self)
        self._list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 4))
        self._list_frame.grid_columnconfigure(0, weight=1)

        # ── Feedback bar ──
        self._status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#16a34a", "#22c55e"),
        )
        self._status_label.pack(fill="x", padx=16, pady=(0, 10))

        self._build_list()

        # Bind Escape to close
        self.bind("<Escape>", lambda e: self.destroy())

    # ── internals ──

    def _clear_search(self):
        self._search_var.set("")
        self._search_entry.focus_set()

    def _on_search(self, *_):
        keyword = self._search_var.get().strip().lower()
        if keyword:
            self._filtered = [m for m in self._models if keyword in m.lower()]
        else:
            self._filtered = self._models[:]
        self._build_list()

    def _build_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        if not self._filtered:
            lbl = ctk.CTkLabel(
                self._list_frame,
                text="无匹配模型",
                font=ctk.CTkFont(size=13),
                text_color=("#888888", "#aaaaaa"),
            )
            lbl.grid(row=0, column=0, pady=20)
            self._count_label.configure(
                text=f"共 {len(self._models)} 个模型 | 筛选: 0"
            )
            return

        self._count_label.configure(
            text=f"共 {len(self._models)} 个模型 | 筛选: {len(self._filtered)}"
        )

        for model in self._filtered:
            lbl = ctk.CTkLabel(
                self._list_frame,
                text=model,
                anchor="w",
                cursor="hand2",
                text_color=("#1a1a1a", "#e0e0e0"),
            )
            lbl.grid(row=self._list_frame.grid_size()[1], column=0, padx=6, pady=1, sticky="ew")
            lbl.bind("<Button-1>", lambda e, m=model: self._copy(m))

    def _copy(self, model: str):
        self.clipboard_clear()
        self.clipboard_append(model)
        self._status_label.configure(text=f"✓ 已复制: {model}")
        self.after(2000, lambda: self._status_label.configure(text=""))
