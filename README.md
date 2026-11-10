# Sistema de Usuários (Python + Tkinter + SQLite)

Aplicação desktop moderna para cadastro, login e gerenciamento de usuários.

## ✨ Melhorias desta versão

- Interface com tema escuro, cards e botões com hover
- Código organizado em classes (`App`, `EditUserDialog`)
- Listagem em **Treeview** (tabela) em vez de texto puro
- **Edição** de usuários (nome, e-mail e senha opcional)
- Confirmação antes de excluir
- Busca em tempo real (ao digitar)
- Mostrar/ocultar senha
- Validação de e-mail com regex
- Funções de auth retornam `(sucesso, mensagem)` de forma previsível
- E-mail único no banco (`UNIQUE`)
- Contador de usuários e status colorido
- Janela centralizada e responsiva

## 🚀 Funcionalidades

- Cadastro com validação
- Login por nome ou e-mail
- Listagem ordenada
- Busca por nome/e-mail
- Edição de usuário
- Exclusão com confirmação
- Sessão simples após login

## 🛠 Tecnologias

- Python 3
- Tkinter / ttk
- SQLite
- hashlib (SHA-256)

## 📁 Estrutura

```
sistema-usuarios/
├── app.py          # Interface gráfica
├── auth.py         # Autenticação e CRUD
├── database.py     # Conexão e schema
├── usuarios.db     # Criado automaticamente na 1ª execução
└── README.md
```

## ▶ Como executar

```bash
cd sistema-usuarios
python app.py
```

Requer Python 3.10+ (usa `str | None` e `list[dict]`). Em versões antigas, ajuste as anotações ou rode com `from __future__ import annotations` (já incluso).

## 🔐 Observação de segurança

As senhas são armazenadas com **SHA-256** (sem salt). Para produção, use `bcrypt` ou `argon2`. Este projeto é voltado a aprendizado e portfólio.
