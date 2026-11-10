"""Regras de autenticação e CRUD de usuários."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime

from database import conectar


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def _validar_campos(nome: str, email: str, senha: str, exigir_senha: bool = True) -> str | None:
    nome = nome.strip()
    email = email.strip().lower()

    if not nome or not email or (exigir_senha and not senha):
        return "Preencha todos os campos."

    if len(nome) < 3:
        return "O nome precisa ter pelo menos 3 caracteres."

    if not EMAIL_RE.match(email):
        return "E-mail inválido."

    if exigir_senha and len(senha) < 4:
        return "A senha precisa ter pelo menos 4 caracteres."

    return None


def cadastrar(nome: str, email: str, senha: str) -> tuple[bool, str]:
    erro = _validar_campos(nome, email, senha)
    if erro:
        return False, erro

    nome = nome.strip()
    email = email.strip().lower()
    senha_hash = _hash_senha(senha)
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    try:
        with conectar() as conn:
            existe = conn.execute(
                "SELECT 1 FROM usuarios WHERE email = ?", (email,)
            ).fetchone()
            if existe:
                return False, "Este e-mail já está cadastrado."

            conn.execute(
                "INSERT INTO usuarios (nome, email, senha, data) VALUES (?, ?, ?, ?)",
                (nome, email, senha_hash, agora),
            )
            conn.commit()
        return True, "Usuário cadastrado com sucesso!"
    except Exception as exc:  # noqa: BLE001
        return False, f"Erro ao cadastrar: {exc}"


def login(identificador: str, senha: str) -> tuple[bool, str, dict | None]:
    identificador = identificador.strip()
    if not identificador or not senha:
        return False, "Informe nome/e-mail e senha.", None

    senha_hash = _hash_senha(senha)

    with conectar() as conn:
        row = conn.execute(
            """
            SELECT id, nome, email, senha, data
            FROM usuarios
            WHERE nome = ? OR email = ?
            """,
            (identificador, identificador.lower()),
        ).fetchone()

    if not row or row["senha"] != senha_hash:
        return False, "Nome/e-mail ou senha incorretos.", None

    usuario = {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "data": row["data"],
    }
    return True, f"Bem-vindo(a), {usuario['nome']}!", usuario


def listar_usuarios(termo: str = "") -> list[dict]:
    termo = termo.strip()
    with conectar() as conn:
        if termo:
            rows = conn.execute(
                """
                SELECT id, nome, email, data
                FROM usuarios
                WHERE nome LIKE ? OR email LIKE ?
                ORDER BY nome COLLATE NOCASE
                """,
                (f"%{termo}%", f"%{termo}%"),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, nome, email, data
                FROM usuarios
                ORDER BY nome COLLATE NOCASE
                """
            ).fetchall()

    return [dict(r) for r in rows]


def obter_por_email(email: str) -> dict | None:
    with conectar() as conn:
        row = conn.execute(
            "SELECT id, nome, email, data FROM usuarios WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    return dict(row) if row else None


def editar_usuario(
    email_atual: str,
    novo_nome: str,
    novo_email: str,
    nova_senha: str = "",
) -> tuple[bool, str]:
    email_atual = email_atual.strip().lower()
    novo_nome = novo_nome.strip()
    novo_email = novo_email.strip().lower()

    erro = _validar_campos(novo_nome, novo_email, nova_senha, exigir_senha=bool(nova_senha))
    if erro:
        return False, erro

    with conectar() as conn:
        atual = conn.execute(
            "SELECT id FROM usuarios WHERE email = ?", (email_atual,)
        ).fetchone()
        if not atual:
            return False, "Usuário não encontrado."

        conflito = conn.execute(
            "SELECT id FROM usuarios WHERE email = ? AND email != ?",
            (novo_email, email_atual),
        ).fetchone()
        if conflito:
            return False, "O novo e-mail já está em uso."

        if nova_senha:
            conn.execute(
                "UPDATE usuarios SET nome = ?, email = ?, senha = ? WHERE email = ?",
                (novo_nome, novo_email, _hash_senha(nova_senha), email_atual),
            )
        else:
            conn.execute(
                "UPDATE usuarios SET nome = ?, email = ? WHERE email = ?",
                (novo_nome, novo_email, email_atual),
            )
        conn.commit()

    return True, "Usuário atualizado com sucesso!"


def deletar_usuario(email: str) -> tuple[bool, str]:
    email = email.strip().lower()
    if not email:
        return False, "Informe o e-mail do usuário."

    with conectar() as conn:
        cursor = conn.execute("DELETE FROM usuarios WHERE email = ?", (email,))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Usuário não encontrado."

    return True, "Usuário removido com sucesso!"


def total_usuarios() -> int:
    with conectar() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()
    return int(row["total"]) if row else 0
