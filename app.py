"""Sistema de Usuários — interface moderna com Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import auth
from database import criar_tabela


# ---------------------------------------------------------------------------
# Tema / cores
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#0f1419",
    "surface": "#1a2332",
    "surface2": "#243044",
    "border": "#2e3d55",
    "text": "#e8eef7",
    "muted": "#94a3b8",
    "primary": "#3b82f6",
    "primary_hover": "#60a5fa",
    "success": "#22c55e",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "input_bg": "#0b1220",
}


class ModernButton(tk.Button):
    """Botão com hover simples."""

    def __init__(self, master, bg_color, **kwargs):
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("cursor", "hand2")
        kwargs.setdefault("font", ("Segoe UI", 11, "bold"))
        kwargs.setdefault("fg", "white")
        kwargs.setdefault("activeforeground", "white")
        kwargs.setdefault("padx", 14)
        kwargs.setdefault("pady", 8)
        super().__init__(master, bg=bg_color, activebackground=bg_color, **kwargs)
        self._bg = bg_color
        self.bind("<Enter>", lambda _e: self.configure(bg=self._lighten(bg_color)))
        self.bind("<Leave>", lambda _e: self.configure(bg=self._bg))

    @staticmethod
    def _lighten(hex_color: str) -> str:
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        r, g, b = min(255, r + 20), min(255, g + 20), min(255, b + 20)
        return f"#{r:02x}{g:02x}{b:02x}"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        criar_tabela()

        self.title("Sistema de Usuários")
        self.geometry("780x640")
        self.minsize(680, 560)
        self.configure(bg=COLORS["bg"])
        self._center_window(780, 640)

        self.usuario_logado: dict | None = None
        self._show_senha = tk.BooleanVar(value=False)

        self._setup_styles()
        self._build_layout()
        self._mostrar_login()

    # ------------------------------------------------------------------
    # Utilitários de UI
    # ------------------------------------------------------------------
    def _center_window(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=COLORS["surface"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["surface"],
            borderwidth=0,
            rowheight=28,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["surface2"],
            foreground=COLORS["text"],
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", "white")],
        )
        style.configure(
            "TScrollbar",
            background=COLORS["surface2"],
            troughcolor=COLORS["bg"],
            borderwidth=0,
            arrowsize=14,
        )

    def _card(self, parent: tk.Widget, **kwargs) -> tk.Frame:
        return tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            **kwargs,
        )

    def _label(self, parent: tk.Widget, text: str, **kwargs) -> tk.Label:
        opts = {
            "bg": kwargs.pop("bg", COLORS["surface"]),
            "fg": kwargs.pop("fg", COLORS["text"]),
            "font": kwargs.pop("font", ("Segoe UI", 10)),
        }
        opts.update(kwargs)
        return tk.Label(parent, text=text, **opts)

    def _entry(self, parent: tk.Widget, show: str | None = None, width: int = 32) -> tk.Entry:
        entry = tk.Entry(
            parent,
            font=("Segoe UI", 11),
            width=width,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"],
        )
        if show is not None:
            entry.configure(show=show)
        return entry

    def _set_status(self, texto: str, ok: bool | None = None) -> None:
        self.status_label.configure(text=texto)
        if ok is True:
            self.status_label.configure(fg=COLORS["success"])
        elif ok is False:
            self.status_label.configure(fg=COLORS["danger"])
        else:
            self.status_label.configure(fg=COLORS["muted"])

    # ------------------------------------------------------------------
    # Layout base
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        # Header
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=28, pady=(22, 8))

        tk.Label(
            header,
            text="Sistema de Usuários",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor="w")

        self.subtitle = tk.Label(
            header,
            text="Cadastro, login e gerenciamento",
            font=("Segoe UI", 11),
            bg=COLORS["bg"],
            fg=COLORS["muted"],
        )
        self.subtitle.pack(anchor="w", pady=(2, 0))

        # Área principal (troca de telas)
        self.main = tk.Frame(self, bg=COLORS["bg"])
        self.main.pack(fill="both", expand=True, padx=28, pady=12)

        # Status bar
        self.status_label = tk.Label(
            self,
            text="",
            font=("Segoe UI", 10),
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            anchor="w",
        )
        self.status_label.pack(fill="x", padx=28, pady=(0, 16))

        self.frame_login: tk.Frame | None = None
        self.frame_admin: tk.Frame | None = None

    def _limpar_main(self) -> None:
        for child in self.main.winfo_children():
            child.destroy()

    # ------------------------------------------------------------------
    # Tela de login / cadastro
    # ------------------------------------------------------------------
    def _mostrar_login(self) -> None:
        self.usuario_logado = None
        self._limpar_main()
        self.subtitle.configure(text="Cadastro, login e gerenciamento")

        card = self._card(self.main)
        card.pack(fill="x", pady=8)

        inner = tk.Frame(card, bg=COLORS["surface"])
        inner.pack(fill="x", padx=24, pady=24)

        self._label(
            inner,
            "Acesse sua conta ou crie um novo usuário",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 16))

        # Campos
        form = tk.Frame(inner, bg=COLORS["surface"])
        form.pack(fill="x")

        self._label(form, "Nome (ou e-mail no login)").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.entrada_nome = self._entry(form)
        self.entrada_nome.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self._label(form, "E-mail (apenas no cadastro)").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.entrada_email = self._entry(form)
        self.entrada_email.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        self._label(form, "Senha").grid(row=4, column=0, sticky="w", pady=(0, 4))

        senha_row = tk.Frame(form, bg=COLORS["surface"])
        senha_row.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        form.columnconfigure(0, weight=1)

        self.entrada_senha = self._entry(senha_row, show="*")
        self.entrada_senha.pack(side="left", fill="x", expand=True)

        tk.Checkbutton(
            senha_row,
            text="Mostrar",
            variable=self._show_senha,
            command=self._toggle_senha,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            selectcolor=COLORS["surface2"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["text"],
            font=("Segoe UI", 9),
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))

        # Botões
        btns = tk.Frame(inner, bg=COLORS["surface"])
        btns.pack(fill="x", pady=(12, 0))

        ModernButton(
            btns,
            COLORS["success"],
            text="Cadastrar",
            command=self._acao_cadastrar,
            width=14,
        ).pack(side="left", padx=(0, 8))

        ModernButton(
            btns,
            COLORS["primary"],
            text="Entrar",
            command=self._acao_login,
            width=14,
        ).pack(side="left")

        self.entrada_nome.focus_set()
        self.bind("<Return>", lambda _e: self._acao_login())

    def _toggle_senha(self) -> None:
        self.entrada_senha.configure(show="" if self._show_senha.get() else "*")

    def _acao_cadastrar(self) -> None:
        ok, msg = auth.cadastrar(
            self.entrada_nome.get(),
            self.entrada_email.get(),
            self.entrada_senha.get(),
        )
        self._set_status(msg, ok)
        if ok:
            self.entrada_nome.delete(0, tk.END)
            self.entrada_email.delete(0, tk.END)
            self.entrada_senha.delete(0, tk.END)

    def _acao_login(self) -> None:
        ok, msg, usuario = auth.login(self.entrada_nome.get(), self.entrada_senha.get())
        self._set_status(msg, ok)
        if ok and usuario:
            self.usuario_logado = usuario
            self._mostrar_admin()

    # ------------------------------------------------------------------
    # Painel admin
    # ------------------------------------------------------------------
    def _mostrar_admin(self) -> None:
        self._limpar_main()
        nome = self.usuario_logado["nome"] if self.usuario_logado else ""
        self.subtitle.configure(text=f"Logado como {nome}")

        # Top bar
        top = tk.Frame(self.main, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 12))

        self._label(
            top,
            f"👥  {auth.total_usuarios()} usuário(s) cadastrado(s)",
            bg=COLORS["bg"],
            font=("Segoe UI", 11),
            fg=COLORS["muted"],
        ).pack(side="left")

        ModernButton(
            top,
            COLORS["warning"],
            text="Sair",
            command=self._logout,
            fg="#111",
            activeforeground="#111",
            width=10,
        ).pack(side="right")

        # Busca
        search_card = self._card(self.main)
        search_card.pack(fill="x", pady=(0, 12))

        search_inner = tk.Frame(search_card, bg=COLORS["surface"])
        search_inner.pack(fill="x", padx=16, pady=12)

        self._label(search_inner, "Buscar por nome ou e-mail").pack(anchor="w")

        row = tk.Frame(search_inner, bg=COLORS["surface"])
        row.pack(fill="x", pady=(6, 0))

        self.entrada_busca = self._entry(row, width=40)
        self.entrada_busca.pack(side="left", fill="x", expand=True)
        self.entrada_busca.bind("<KeyRelease>", lambda _e: self._atualizar_lista())

        ModernButton(
            row,
            COLORS["primary"],
            text="Buscar",
            command=self._atualizar_lista,
            width=10,
        ).pack(side="left", padx=(8, 0))

        ModernButton(
            row,
            COLORS["surface2"],
            text="Limpar",
            command=self._limpar_busca,
            width=10,
        ).pack(side="left", padx=(6, 0))

        # Tabela
        table_card = self._card(self.main)
        table_card.pack(fill="both", expand=True, pady=(0, 12))

        table_inner = tk.Frame(table_card, bg=COLORS["surface"])
        table_inner.pack(fill="both", expand=True, padx=12, pady=12)

        cols = ("id", "nome", "email", "data")
        self.tree = ttk.Treeview(
            table_inner,
            columns=cols,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("email", text="E-mail")
        self.tree.heading("data", text="Cadastro")

        self.tree.column("id", width=50, anchor="center", stretch=False)
        self.tree.column("nome", width=180)
        self.tree.column("email", width=220)
        self.tree.column("data", width=130, anchor="center")

        scroll = ttk.Scrollbar(table_inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Ações
        actions = tk.Frame(self.main, bg=COLORS["bg"])
        actions.pack(fill="x")

        ModernButton(
            actions,
            COLORS["primary"],
            text="Atualizar lista",
            command=self._atualizar_lista,
            width=14,
        ).pack(side="left", padx=(0, 8))

        ModernButton(
            actions,
            COLORS["warning"],
            text="Editar selecionado",
            command=self._editar_selecionado,
            fg="#111",
            activeforeground="#111",
            width=16,
        ).pack(side="left", padx=(0, 8))

        ModernButton(
            actions,
            COLORS["danger"],
            text="Excluir selecionado",
            command=self._excluir_selecionado,
            width=16,
        ).pack(side="left")

        self._atualizar_lista()
        self.unbind("<Return>")

    def _limpar_busca(self) -> None:
        self.entrada_busca.delete(0, tk.END)
        self._atualizar_lista()

    def _atualizar_lista(self) -> None:
        termo = self.entrada_busca.get() if hasattr(self, "entrada_busca") else ""
        usuarios = auth.listar_usuarios(termo)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for u in usuarios:
            self.tree.insert(
                "",
                "end",
                iid=str(u["id"]),
                values=(u["id"], u["nome"], u["email"], u["data"]),
            )

        total = auth.total_usuarios()
        filtrados = len(usuarios)
        if termo.strip():
            self._set_status(f"{filtrados} resultado(s) · {total} no total", True)
        else:
            self._set_status(f"{total} usuário(s) no sistema", True)

    def _usuario_selecionado(self) -> dict | None:
        sel = self.tree.selection()
        if not sel:
            self._set_status("Selecione um usuário na tabela.", False)
            return None
        valores = self.tree.item(sel[0], "values")
        return {
            "id": valores[0],
            "nome": valores[1],
            "email": valores[2],
            "data": valores[3],
        }

    def _excluir_selecionado(self) -> None:
        user = self._usuario_selecionado()
        if not user:
            return

        if self.usuario_logado and user["email"] == self.usuario_logado["email"]:
            if not messagebox.askyesno(
                "Confirmar",
                "Você está prestes a excluir a própria conta e será desconectado.\nContinuar?",
            ):
                return
        else:
            if not messagebox.askyesno(
                "Confirmar exclusão",
                f"Excluir permanentemente o usuário\n{user['nome']} ({user['email']})?",
            ):
                return

        ok, msg = auth.deletar_usuario(user["email"])
        self._set_status(msg, ok)

        if ok and self.usuario_logado and user["email"] == self.usuario_logado["email"]:
            self._logout()
            return

        self._atualizar_lista()

    def _editar_selecionado(self) -> None:
        user = self._usuario_selecionado()
        if not user:
            return
        EditUserDialog(self, user, on_saved=self._atualizar_lista)

    def _logout(self) -> None:
        self.usuario_logado = None
        self._set_status("Sessão encerrada.")
        self._mostrar_login()


class EditUserDialog(tk.Toplevel):
    """Modal simples para editar usuário."""

    def __init__(self, master: App, user: dict, on_saved) -> None:
        super().__init__(master)
        self.user = user
        self.on_saved = on_saved
        self.app = master

        self.title("Editar usuário")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        w, h = 420, 360
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        card = tk.Frame(
            self,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        inner = tk.Frame(card, bg=COLORS["surface"])
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            inner,
            text="Editar usuário",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(anchor="w", pady=(0, 14))

        self.nome = self._field(inner, "Nome", user["nome"])
        self.email = self._field(inner, "E-mail", user["email"])
        self.senha = self._field(inner, "Nova senha (opcional)", "", show="*")

        btns = tk.Frame(inner, bg=COLORS["surface"])
        btns.pack(fill="x", pady=(16, 0))

        ModernButton(
            btns,
            COLORS["primary"],
            text="Salvar",
            command=self._salvar,
            width=12,
        ).pack(side="left", padx=(0, 8))

        ModernButton(
            btns,
            COLORS["surface2"],
            text="Cancelar",
            command=self.destroy,
            width=12,
        ).pack(side="left")

        self.status = tk.Label(
            inner,
            text="",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        )
        self.status.pack(anchor="w", pady=(12, 0))

    def _field(self, parent, label: str, value: str, show: str | None = None) -> tk.Entry:
        tk.Label(
            parent,
            text=label,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        entry = tk.Entry(
            parent,
            font=("Segoe UI", 11),
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"],
        )
        if show is not None:
            entry.configure(show=show)
        entry.insert(0, value)
        entry.pack(fill="x", pady=(4, 10))
        return entry

    def _salvar(self) -> None:
        ok, msg = auth.editar_usuario(
            self.user["email"],
            self.nome.get(),
            self.email.get(),
            self.senha.get(),
        )
        self.status.configure(
            text=msg,
            fg=COLORS["success"] if ok else COLORS["danger"],
        )
        if ok:
            self.on_saved()
            # Atualiza sessão se editou a si mesmo
            if self.app.usuario_logado and self.app.usuario_logado["email"] == self.user["email"]:
                self.app.usuario_logado["nome"] = self.nome.get().strip()
                self.app.usuario_logado["email"] = self.email.get().strip().lower()
                self.app.subtitle.configure(
                    text=f"Logado como {self.app.usuario_logado['nome']}"
                )
            self.after(600, self.destroy)


if __name__ == "__main__":
    app = App()
    app.mainloop()
