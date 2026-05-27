import tkinter as tk
from database import criar_tabela, conectar
from auth import cadastrar, login as auth_login, deletar_usuario

criar_tabela()

# =========================
# JANELA
# =========================
janela = tk.Tk()
janela.title("Sistema de Usuários")
janela.geometry("500x600")
janela.configure(bg="#1e1e1e")

# =========================
# TÍTULO
# =========================
titulo = tk.Label(
    janela,
    text="SISTEMA DE USUÁRIOS",
    font=("Arial", 18, "bold"),
    bg="#1e1e1e",
    fg="white"
)
titulo.pack(pady=15)

subtitulo = tk.Label(
    janela,
    text="Gerenciamento de usuários",
    font=("Arial", 11),
    bg="#1e1e1e",
    fg="white"
)
subtitulo.pack(pady=5)

# =========================
# FRAMES LOGIN
# =========================
frame_nome = tk.Frame(janela, bg="#1e1e1e")
frame_nome.pack(pady=5)

label_nome = tk.Label(
    frame_nome,
    text="Nome",
    bg="#1e1e1e",
    fg="white",
    width=10,
    anchor="e"
)
label_nome.pack(side="left", padx=5)

entrada_nome = tk.Entry(frame_nome, font=("Arial", 12), width=25)
entrada_nome.pack(side="left")

frame_email = tk.Frame(janela, bg="#1e1e1e")
frame_email.pack(pady=5)

label_email = tk.Label(
    frame_email,
    text="Email",
    bg="#1e1e1e",
    fg="white",
    width=10,
    anchor="e"
)
label_email.pack(side="left", padx=5)

entrada_email = tk.Entry(frame_email, font=("Arial", 12), width=25)
entrada_email.pack(side="left")

frame_senha = tk.Frame(janela, bg="#1e1e1e")
frame_senha.pack(pady=5)

label_senha = tk.Label(
    frame_senha,
    text="Senha",
    bg="#1e1e1e",
    fg="white",
    width=10,
    anchor="e"
)
label_senha.pack(side="left", padx=5)

entrada_senha = tk.Entry(
    frame_senha,
    show="*",
    font=("Arial", 12),
    width=25
)
entrada_senha.pack(side="left")

# =========================
# STATUS
# =========================
label_status = tk.Label(
    janela,
    text="",
    bg="#1e1e1e",
    fg="white",
    font=("Arial", 11)
)
label_status.pack(pady=10)

# =========================
# PAINEL ADMIN
# =========================
frame_admin = tk.Frame(janela, bg="#1e1e1e")

entrada_busca = tk.Entry(
    frame_admin,
    font=("Arial", 12),
    width=25
)
entrada_busca.pack(pady=5)

label_resultado = tk.Text(
    frame_admin,
    height=12,
    width=58,
    bg="#0f0f0f",
    fg="white",
    font=("Consolas", 10)
)
label_resultado.pack(pady=10)

# =========================
# FUNÇÕES
# =========================
def ver_usuarios():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nome, email, data FROM usuarios")
    dados = cursor.fetchall()

    conn.close()

    label_resultado.config(state="normal")
    label_resultado.delete("1.0", tk.END)

    label_resultado.insert(
        tk.END,
        "NOME | EMAIL | DATA\n"
    )
    label_resultado.insert(
        tk.END,
        "-" * 50 + "\n"
    )

    for u in dados:
        linha = f"{u[0]} | {u[1]} | {u[2]}\n"
        label_resultado.insert(tk.END, linha)

    label_resultado.config(state="disabled")


def buscar_usuario():
    termo = entrada_busca.get().strip()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, email, data
        FROM usuarios
        WHERE nome LIKE ? OR email LIKE ?
    """, (f"%{termo}%", f"%{termo}%"))

    dados = cursor.fetchall()

    conn.close()

    label_resultado.config(state="normal")
    label_resultado.delete("1.0", tk.END)

    for u in dados:
        linha = f"{u[0]} | {u[1]} | {u[2]}\n"
        label_resultado.insert(tk.END, linha)

    label_resultado.config(state="disabled")


def acao_deletar():
    email = entrada_busca.get().strip()

    resultado = deletar_usuario(email)

    label_status.config(text=resultado)

    ver_usuarios()


def abrir_cadastro():
    nome = entrada_nome.get()
    email = entrada_email.get()
    senha = entrada_senha.get()

    resultado = cadastrar(nome, email, senha)

    label_status.config(text=resultado)

    if "sucesso" in resultado.lower():
        label_status.config(fg="green")

        entrada_nome.delete(0, tk.END)
        entrada_email.delete(0, tk.END)
        entrada_senha.delete(0, tk.END)

    else:
        label_status.config(fg="red")


def abrir_login():
    identificador = entrada_nome.get()
    senha = entrada_senha.get()

    resultado = auth_login(identificador, senha)

    label_status.config(text=resultado)

    if "bem-vindo" not in resultado.lower():
        label_status.config(fg="red")
        return

    label_status.config(fg="green")

    # ESCONDE LOGIN
    frame_nome.pack_forget()
    frame_email.pack_forget()
    frame_senha.pack_forget()

    btn_cadastrar.pack_forget()
    btn_login.pack_forget()

    # MOSTRA ADMIN
    frame_admin.pack(pady=15)

    ver_usuarios()


def voltar_login():
    frame_admin.pack_forget()

    frame_nome.pack(pady=5)
    frame_email.pack(pady=5)
    frame_senha.pack(pady=5)

    btn_cadastrar.pack(pady=5)
    btn_login.pack(pady=5)

    label_status.config(text="")


# =========================
# BOTÕES LOGIN
# =========================
btn_cadastrar = tk.Button(
    janela,
    text="Cadastrar",
    command=abrir_cadastro,
    font=("Arial", 12),
    width=20,
    bg="#28a745",
    fg="white"
)
btn_cadastrar.pack(pady=5)

btn_login = tk.Button(
    janela,
    text="Login",
    command=abrir_login,
    font=("Arial", 12),
    width=20,
    bg="#007bff",
    fg="white"
)
btn_login.pack(pady=5)

# =========================
# BOTÕES ADMIN
# =========================
btn_listar = tk.Button(
    frame_admin,
    text="Listar usuários",
    command=ver_usuarios,
    font=("Arial", 12),
    width=20,
    bg="#6c757d",
    fg="white"
)
btn_listar.pack(pady=5)

btn_buscar = tk.Button(
    frame_admin,
    text="Buscar usuário",
    command=buscar_usuario,
    font=("Arial", 12),
    width=20,
    bg="#17a2b8",
    fg="white"
)
btn_buscar.pack(pady=5)

btn_deletar = tk.Button(
    frame_admin,
    text="Deletar usuário",
    command=acao_deletar,
    font=("Arial", 12),
    width=20,
    bg="#dc3545",
    fg="white"
)
btn_deletar.pack(pady=5)

btn_voltar = tk.Button(
    frame_admin,
    text="Voltar",
    command=voltar_login,
    font=("Arial", 12),
    width=20,
    bg="#ffc107",
    fg="black"
)
btn_voltar.pack(pady=5)

btn_sair = tk.Button(
    frame_admin,
    text="Encerrar",
    command=janela.quit,
    font=("Arial", 12),
    width=20,
    bg="#dc3545",
    fg="white"
)

btn_sair.pack(pady=10)

# =========================
# LOOP
# =========================
janela.mainloop()