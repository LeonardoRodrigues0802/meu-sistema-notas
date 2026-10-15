import tkinter as tk
from tkinter import ttk

import banco
import utilidades


class SistemaNotasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Notas Escolares")
        self.root.geometry("1100x700")
        self.root.minsize(1000, 650)
        self.tema_escuro = True
        self.widgets_tema = []
        self.root.configure(bg="#0b1020")
        self.root.option_add("*Font", "Arial 10")
        self.usuario_logado = None

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Arial", 11, "bold"), padding=8)
        self.style.configure("TEntry", font=("Arial", 11))
        self.style.configure("TLabel", background="#0b1020", foreground="#e5ecff")
        self.style.map(
            "TButton",
            background=[("active", "#1d4ed8")],
            foreground=[("active", "white")],
        )

        self.frames = {}
        self.criar_frames()
        self.aplicar_tema()
        self.mostrar_tela("login")

    def registrar_widget_tema(self, widget, tipo="geral"):
        self.widgets_tema.append((widget, tipo))

    def aplicar_tema(self):
        if self.tema_escuro:
            bg_geral = "#0b1020"
            panel = "#121a2d"
            text = "#eaf1ff"
            field = "#0f172a"
            field_text = "#f8fafc"
            btn_switch = "#e2e8f0"
            btn_switch_fg = "#111827"
        else:
            bg_geral = "#edf3ff"
            panel = "#f5f9ff"
            text = "#1f2937"
            field = "#f3f7ff"
            field_text = "#1f2937"
            btn_switch = "#1f2937"
            btn_switch_fg = "#f8fafc"

        self.root.configure(bg=bg_geral)

        for frame in self.frames.values():
            frame.configure(bg=bg_geral)

        for widget, tipo in self.widgets_tema:
            try:
                classe = widget.winfo_class()
            except Exception:
                continue

            if tipo == "botao_tema":
                widget.configure(bg=btn_switch, fg=btn_switch_fg)
                continue

            if classe in {"Frame", "Labelframe"}:
                widget.configure(bg=panel)
            elif classe == "Label":
                widget.configure(bg=panel, fg=text)
            elif classe == "Entry":
                widget.configure(bg=field, fg=field_text, insertbackground=text)
            elif classe == "Text":
                widget.configure(bg=field, fg=text)
            elif classe == "Button":
                bg_atual = widget.cget("bg")
                if bg_atual in {"#2563eb", "#1d4ed8", "#3b82f6", "#0f766e", "#ef4444", "#7c3aed", "#b91c1c", "#1f9d55", "#475569", "#d93025", "#f59e0b", "#10b981"}:
                    widget.configure(fg="white")
                else:
                    widget.configure(bg=panel, fg=text)

        if hasattr(self, "btn_tema"):
            self.btn_tema.config(text="Modo claro" if self.tema_escuro else "Modo escuro", bg=btn_switch, fg=btn_switch_fg)

        self.root.update_idletasks()
        self.root.update()

    def alternar_tema(self):
        self.tema_escuro = not self.tema_escuro
        self.aplicar_tema()

    def criar_frames(self):
        self.frames["login"] = self.criar_frame_login()
        self.frames["menu_admin"] = self.criar_frame_menu()
        self.frames["menu"] = self.frames["menu_admin"]
        self.frames["menu_funcionario"] = self.criar_frame_menu_funcionario()
        self.frames["cadastro"] = self.criar_frame_cadastro()
        self.frames["lista"] = self.criar_frame_lista()
        self.frames["buscar"] = self.criar_frame_buscar()
        self.frames["atualizar"] = self.criar_frame_atualizar()
        self.frames["remover"] = self.criar_frame_remover()
        self.frames["relatorio"] = self.criar_frame_relatorio()
        self.frames["usuarios"] = self.criar_frame_usuarios()
        self.frames["logs"] = self.criar_frame_logs()

    def mostrar_tela(self, nome):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[nome].pack(fill="both", expand=True)

    def criar_botao_acao(self, pai, texto, comando, cor_fundo, cor_texto="white", largura=28, altura=2, fonte=("Arial", 12, "bold"), borda=0):
        return tk.Button(
            pai,
            text=texto,
            width=largura,
            height=altura,
            font=fonte,
            bg=cor_fundo,
            fg=cor_texto,
            relief="flat",
            bd=borda,
            cursor="hand2",
            activebackground="#0f172a",
            activeforeground="white",
            command=comando,
        )

    def criar_frame_login(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=30, pady=28)
        painel.pack(fill="both", expand=True, padx=350, pady=120)
        self.registrar_widget_tema(painel, "frame")

        titulo = tk.Label(painel, text="🔐 Login com Pendrive", font=("Arial", 26, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(pady=(10, 20))
        self.registrar_widget_tema(titulo, "label")

        campos = []
        for label_text, chave in [("Usuário", "usuario"), ("Senha", "senha")]:
            linha = tk.Frame(painel, bg="#121a2d")
            linha.pack(pady=8)
            self.registrar_widget_tema(linha, "frame")

            lbl = tk.Label(linha, text=label_text, font=("Arial", 11, "bold"), bg="#121a2d", width=12, anchor="w", fg="#e2e8f0")
            lbl.pack(side="left", padx=(0, 10))
            self.registrar_widget_tema(lbl, "label")

            entry = tk.Entry(linha, width=28, font=("Arial", 11), show="*" if chave == "senha" else "", bd=1, relief="solid", bg="#0f172a", fg="#f8fafc", insertbackground="white", highlightthickness=1, highlightbackground="#24314d")
            entry.pack(side="left")
            self.registrar_widget_tema(entry, "entry")
            campos.append(entry)

        self.login_usuario = campos[0]
        self.login_senha = campos[1]

        btn_entrar = self.criar_botao_acao(painel, "➡️ Entrar", self.efetuar_login, "#2563eb")
        btn_entrar.pack(pady=(15, 8))
        self.registrar_widget_tema(btn_entrar, "botao")

        self.msg_login = tk.Label(painel, text="", font=("Arial", 10, "bold"), bg="#121a2d", fg="#fca5a5")
        self.msg_login.pack(pady=10)
        self.registrar_widget_tema(self.msg_login, "label")

        return frame

    def efetuar_login(self):
        usuario = self.login_usuario.get().strip()
        senha = self.login_senha.get().strip()

        conta = banco.autenticar_usuario(usuario, senha)
        if not conta:
            self.msg_login.config(text="Erro: Credenciais inválidas ou pendrive ausente.", fg="#fca5a5")
            return

        self.usuario_logado = conta
        self.msg_login.config(text=f"Bem-vindo, {conta['tipo']}.", fg="#7ef0a6")
        self.login_usuario.delete(0, tk.END)
        self.login_senha.delete(0, tk.END)
        self.atualizar_info_usuario()
        if conta["tipo"] == "admin":
            self.mostrar_tela("menu")
        else:
            self.mostrar_tela("menu_funcionario")

    def criar_frame_menu(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=28, pady=28, bd=0)
        painel.pack(fill="both", expand=True, padx=90, pady=50)
        self.registrar_widget_tema(painel, "frame")

        cabecalho = tk.Frame(painel, bg="#121a2d")
        cabecalho.pack(fill="x", pady=(10, 20))
        self.registrar_widget_tema(cabecalho, "frame")

        titulo = tk.Label(cabecalho, text="🎓 Sistema de Notas Escolares", font=("Arial", 28, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(anchor="center")
        self.registrar_widget_tema(titulo, "label")

        self.info_usuario = tk.Label(cabecalho, text="", font=("Arial", 11, "bold"), bg="#121a2d", fg="#a7f3d0")
        self.info_usuario.pack(anchor="center", pady=(8, 0))
        self.registrar_widget_tema(self.info_usuario, "label")

        sub = tk.Label(cabecalho, text="📚 Painel acadêmico e gestão de alunos", font=("Arial", 11), bg="#121a2d", fg="#9bb1d1")
        sub.pack(anchor="center", pady=(8, 0))
        self.registrar_widget_tema(sub, "label")

        linha = tk.Frame(painel, bg="#24314d", height=2)
        linha.pack(fill="x", pady=(0, 18))
        self.registrar_widget_tema(linha, "frame")

        self.btn_tema = tk.Button(
            painel,
            text="☀️ Modo claro",
            width=20,
            height=1,
            font=("Arial", 10, "bold"),
            bg="#e2e8f0",
            fg="#111827",
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground="#cbd5e1",
            activeforeground="#111827",
            command=self.alternar_tema,
        )
        self.btn_tema.pack(pady=(0, 12))
        self.registrar_widget_tema(self.btn_tema, "botao_tema")

        botoes = [
            ("📘 Cadastro", self.abrir_cadastro, "#2563eb"),
            ("📋 Lista", self.abrir_lista, "#1d4ed8"),
            ("🔎 Buscar", self.abrir_buscar, "#3b82f6"),
            ("✏️ Atualizar", self.abrir_atualizar, "#0f766e"),
            ("🗑️ Remover", self.abrir_remover, "#ef4444"),
            ("📊 Relatório", self.abrir_relatorio, "#7c3aed"),
            ("🏆 Top 3", self.abrir_top_3, "#f59e0b"),
            ("📄 Exportar TXT", self.exportar_relatorio, "#10b981"),
            ("👥 Usuários", self.abrir_usuarios, "#8b5cf6"),
            ("📝 Logs de acesso", self.abrir_logs, "#0ea5e9"),
            ("🚪 Sair", self.sair, "#b91c1c"),
        ]

        for texto, comando, cor in botoes:
            btn = self.criar_botao_acao(painel, texto, comando, cor)
            btn.pack(pady=7)
            self.registrar_widget_tema(btn, "botao")

        return frame

    def criar_frame_menu_funcionario(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=28, pady=28, bd=0)
        painel.pack(fill="both", expand=True, padx=90, pady=50)
        self.registrar_widget_tema(painel, "frame")

        cabecalho = tk.Frame(painel, bg="#121a2d")
        cabecalho.pack(fill="x", pady=(10, 20))
        self.registrar_widget_tema(cabecalho, "frame")

        titulo = tk.Label(cabecalho, text="👨‍💼 Área do Funcionário", font=("Arial", 28, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(anchor="center")
        self.registrar_widget_tema(titulo, "label")

        self.info_usuario = tk.Label(cabecalho, text="", font=("Arial", 11, "bold"), bg="#121a2d", fg="#a7f3d0")
        self.info_usuario.pack(anchor="center", pady=(8, 0))
        self.registrar_widget_tema(self.info_usuario, "label")

        linha = tk.Frame(painel, bg="#24314d", height=2)
        linha.pack(fill="x", pady=(0, 18))
        self.registrar_widget_tema(linha, "frame")

        botoes = [
            ("📋 Lista", self.abrir_lista, "#1d4ed8"),
            ("🔎 Buscar", self.abrir_buscar, "#3b82f6"),
            ("📊 Relatório", self.abrir_relatorio, "#7c3aed"),
            ("🏆 Top 3", self.abrir_top_3, "#f59e0b"),
            ("🚪 Sair", self.sair, "#b91c1c"),
        ]

        for texto, comando, cor in botoes:
            btn = self.criar_botao_acao(painel, texto, comando, cor)
            btn.pack(pady=9)
            self.registrar_widget_tema(btn, "botao")

        return frame

    def criar_frame_logs(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=25, pady=20)
        painel.pack(fill="both", expand=True, padx=80, pady=40)
        self.registrar_widget_tema(painel, "frame")

        titulo = tk.Label(painel, text="📝 Registro de Acesso", font=("Arial", 24, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(pady=(10, 18))
        self.registrar_widget_tema(titulo, "label")

        self.logs_texto = tk.Text(painel, height=20, width=100, font=("Arial", 10), wrap="word", bg="#0f172a", fg="#f8fafc", highlightthickness=0)
        self.logs_texto.pack(padx=10, pady=8)
        self.logs_texto.config(state="disabled")
        self.registrar_widget_tema(self.logs_texto, "text")

        btn_voltar = self.criar_botao_acao(painel, "⬅️ Voltar", lambda: self.mostrar_tela("menu_admin" if self.usuario_logado and self.usuario_logado["tipo"] == "admin" else "menu_funcionario"), "#475569")
        btn_voltar.pack(pady=10)
        self.registrar_widget_tema(btn_voltar, "botao")

        return frame

    def atualizar_lista_logs(self):
        logs = banco.listar_logs_acesso()
        self.logs_texto.config(state="normal")
        self.logs_texto.delete("1.0", tk.END)

        if not logs:
            self.logs_texto.insert(tk.END, "Nenhum acesso registrado.")
        else:
            for item in logs:
                self.logs_texto.insert(tk.END, f"[{item['data_hora']}] {item['usuario']} | {item['tipo']} | {item['status']}\n")

        self.logs_texto.config(state="disabled")

    def abrir_logs(self):
        if not self.usuario_logado or self.usuario_logado["tipo"] != "admin":
            self.msg_login.config(text="Acesso restrito ao administrador.", fg="#fca5a5")
            self.mostrar_tela("login")
            return
        self.atualizar_lista_logs()
        self.mostrar_tela("logs")

    def atualizar_info_usuario(self):
        if self.usuario_logado:
            tipo = "Administrador" if self.usuario_logado["tipo"] == "admin" else "Funcionário"
            self.info_usuario.config(text=f"Usuário logado: {self.usuario_logado['usuario']} ({tipo})")
        else:
            self.info_usuario.config(text="")

    def abrir_usuarios(self):
        if not self.usuario_logado or self.usuario_logado["tipo"] != "admin":
            self.msg_login.config(text="Acesso restrito apenas para administradores.", fg="#fca5a5")
            self.mostrar_tela("login")
            return

        self.atualizar_lista_usuarios()
        self.mostrar_tela("usuarios")

    def criar_frame_usuarios(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=25, pady=20)
        painel.pack(fill="both", expand=True, padx=120, pady=50)
        self.registrar_widget_tema(painel, "frame")

        titulo = tk.Label(painel, text="👥 Gerenciar Usuários", font=("Arial", 24, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(pady=(10, 18))
        self.registrar_widget_tema(titulo, "label")

        campos = []
        for label_text, chave in [("Usuário", "usuario"), ("Senha", "senha"), ("Tipo", "tipo")]:
            linha = tk.Frame(painel, bg="#121a2d")
            linha.pack(pady=7)
            self.registrar_widget_tema(linha, "frame")

            lbl = tk.Label(linha, text=label_text, font=("Arial", 11, "bold"), bg="#121a2d", width=12, anchor="w", fg="#e2e8f0")
            lbl.pack(side="left", padx=(0, 10))
            self.registrar_widget_tema(lbl, "label")

            if chave == "tipo":
                tipo_var = tk.StringVar(value="funcionario")
                combo = ttk.Combobox(linha, width=27, textvariable=tipo_var, state="readonly", values=["admin", "funcionario"], font=("Arial", 11))
                combo.pack(side="left")
                self.registrar_widget_tema(combo, "entry")
                campos.append(combo)
            else:
                entry = tk.Entry(linha, width=28, font=("Arial", 11), bd=1, relief="solid", bg="#0f172a", fg="#f8fafc", insertbackground="white", highlightthickness=1, highlightbackground="#24314d")
                entry.pack(side="left")
                self.registrar_widget_tema(entry, "entry")
                campos.append(entry)

        self.usuario_form = campos

        btn_cadastrar = self.criar_botao_acao(painel, "✅ Cadastrar usuário", self.cadastrar_usuario, "#1f9d55")
        btn_cadastrar.pack(pady=(18, 8))
        self.registrar_widget_tema(btn_cadastrar, "botao")

        btn_voltar = self.criar_botao_acao(painel, "⬅️ Voltar", lambda: self.mostrar_tela("menu"), "#475569")
        btn_voltar.pack()
        self.registrar_widget_tema(btn_voltar, "botao")

        self.lista_usuarios = tk.Text(painel, height=10, width=70, font=("Arial", 10), wrap="word", bg="#0f172a", fg="#f8fafc", highlightthickness=0)
        self.lista_usuarios.pack(pady=12)
        self.lista_usuarios.config(state="disabled")
        self.registrar_widget_tema(self.lista_usuarios, "text")

        self.msg_usuarios = tk.Label(painel, text="", font=("Arial", 10, "bold"), bg="#121a2d", fg="#7ef0a6")
        self.msg_usuarios.pack(pady=6)
        self.registrar_widget_tema(self.msg_usuarios, "label")

        return frame

    def cadastrar_usuario(self):
        usuario = self.usuario_form[0].get().strip()
        senha = self.usuario_form[1].get().strip()
        tipo = self.usuario_form[2].get().strip().lower()

        if not usuario or not senha:
            self.msg_usuarios.config(text="Preencha usuário e senha.", fg="#fca5a5")
            return

        if tipo not in {"admin", "funcionario"}:
            self.msg_usuarios.config(text="Selecione um tipo válido: admin ou funcionário.", fg="#fca5a5")
            return

        if banco.adicionar_usuario(usuario, senha, tipo):
            self.msg_usuarios.config(text="Usuário cadastrado com sucesso!", fg="#7ef0a6")
            for campo in self.usuario_form:
                if isinstance(campo, ttk.Combobox):
                    campo.set("funcionario")
                else:
                    campo.delete(0, tk.END)
            self.atualizar_lista_usuarios()
        else:
            self.msg_usuarios.config(text="Usuário inválido ou já existente.", fg="#fca5a5")

    def atualizar_lista_usuarios(self):
        usuarios = banco.listar_usuarios()
        self.lista_usuarios.config(state="normal")
        self.lista_usuarios.delete("1.0", tk.END)

        if not usuarios:
            self.lista_usuarios.insert(tk.END, "Nenhum usuário cadastrado.")
        else:
            for conta in usuarios:
                self.lista_usuarios.insert(tk.END, f"{conta['usuario']} | {conta['tipo']}\n")

        self.lista_usuarios.config(state="disabled")

    def criar_frame_cadastro(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=30, pady=26, bd=0)
        painel.pack(fill="both", expand=True, padx=120, pady=50)
        self.registrar_widget_tema(painel, "frame")

        titulo = tk.Label(painel, text="📝 Cadastro de Aluno", font=("Arial", 24, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(pady=(10, 20))
        self.registrar_widget_tema(titulo, "label")

        campos = []
        labels = ["Nome", "Nota 1", "Nota 2", "Nota 3"]
        for label in labels:
            linha = tk.Frame(painel, bg="#121a2d")
            linha.pack(pady=7)
            self.registrar_widget_tema(linha, "frame")

            lbl = tk.Label(linha, text=label, font=("Arial", 11, "bold"), bg="#121a2d", width=12, anchor="w", fg="#e2e8f0")
            lbl.pack(side="left", padx=(0, 10))
            self.registrar_widget_tema(lbl, "label")

            entry = tk.Entry(linha, width=30, font=("Arial", 11), bd=1, relief="solid", bg="#0f172a", fg="#f8fafc", insertbackground="white", highlightthickness=1, highlightbackground="#24314d")
            entry.pack(side="left")
            self.registrar_widget_tema(entry, "entry")
            campos.append(entry)

        self.campos_cadastro = campos

        btn_salvar = self.criar_botao_acao(painel, "💾 Salvar", self.salvar_cadastro, "#1f9d55")
        btn_salvar.pack(pady=(18, 8))
        self.registrar_widget_tema(btn_salvar, "botao")

        btn_voltar = self.criar_botao_acao(painel, "⬅️ Voltar", lambda: self.mostrar_tela("menu"), "#475569")
        btn_voltar.pack()
        self.registrar_widget_tema(btn_voltar, "botao")

        self.msg_cadastro = tk.Label(painel, text="", font=("Arial", 10, "bold"), bg="#121a2d", fg="#7ef0a6")
        self.msg_cadastro.pack(pady=12)
        self.registrar_widget_tema(self.msg_cadastro, "label")

        return frame

    def criar_frame_lista(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=20, pady=18)
        painel.pack(fill="both", expand=True, padx=50, pady=35)
        self.registrar_widget_tema(painel, "frame")

        titulo = tk.Label(painel, text="📋 Lista de Alunos", font=("Arial", 24, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(pady=(5, 10))
        self.registrar_widget_tema(titulo, "label")

        self.lista_texto = tk.Text(painel, height=22, width=110, font=("Arial", 10), wrap="word", bg="#0f172a", fg="#f8fafc", highlightthickness=0)
        self.lista_texto.pack(padx=10, pady=8)
        self.lista_texto.config(state="disabled")
        self.registrar_widget_tema(self.lista_texto, "text")

        btn_voltar = self.criar_botao_acao(painel, "⬅️ Voltar", lambda: self.mostrar_tela("menu" if self.usuario_logado and self.usuario_logado["tipo"] == "admin" else "menu_funcionario"), "#475569")
        btn_voltar.pack(pady=8)
        self.registrar_widget_tema(btn_voltar, "botao")

        return frame

    def criar_frame_buscar(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=20, pady=18)
        painel.pack(fill="both", expand=True, padx=80, pady=35)
        self.registrar_widget_tema(painel, "frame")

        titulo = tk.Label(painel, text="🔎 Buscar Aluno", font=("Arial", 24, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(pady=(5, 18))
        self.registrar_widget_tema(titulo, "label")

        linha = tk.Frame(painel, bg="#121a2d")
        linha.pack(pady=10)
        self.registrar_widget_tema(linha, "frame")

        lbl_nome = tk.Label(linha, text="Nome", font=("Arial", 11, "bold"), bg="#121a2d", width=12, anchor="w", fg="#e2e8f0")
        lbl_nome.pack(side="left", padx=(0, 10))
        self.registrar_widget_tema(lbl_nome, "label")

        self.busca_nome = tk.Entry(linha, width=35, font=("Arial", 11), bd=1, relief="solid", bg="#0f172a", fg="#f8fafc", insertbackground="white", highlightthickness=1, highlightbackground="#24314d")
        self.busca_nome.pack(side="left")
        self.registrar_widget_tema(self.busca_nome, "entry")

        btn_buscar = self.criar_botao_acao(painel, "🔍 Buscar por nome", self.buscar_aluno, "#2563eb")
        btn_buscar.pack(pady=8)
        self.registrar_widget_tema(btn_buscar, "botao")

        btn_status = self.criar_botao_acao(painel, "✅ Buscar por situação", self.buscar_por_situacao, "#10b981")
        btn_status.pack(pady=6)
        self.registrar_widget_tema(btn_status, "botao")

        self.resultado_busca = tk.Text(painel, height=16, width=100, font=("Arial", 10), wrap="word", bg="#0f172a", fg="#f8fafc", highlightthickness=0)
        self.resultado_busca.pack(pady=8)
        self.resultado_busca.config(state="disabled")
        self.registrar_widget_tema(self.resultado_busca, "text")

        btn_voltar = self.criar_botao_acao(painel, "⬅️ Voltar", lambda: self.mostrar_tela("menu" if self.usuario_logado and self.usuario_logado["tipo"] == "admin" else "menu_funcionario"), "#475569")
        btn_voltar.pack(pady=10)
        self.registrar_widget_tema(btn_voltar, "botao")

        return frame

    def criar_frame_atualizar(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=20, pady=18)
        painel.pack(fill="both", expand=True, padx=120, pady=35)
        self.registrar_widget_tema(painel, "frame")

        titulo = tk.Label(painel, text="✏️ Atualizar Notas", font=("Arial", 24, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(pady=(5, 18))
        self.registrar_widget_tema(titulo, "label")

        linha_id = tk.Frame(painel, bg="#121a2d")
        linha_id.pack(pady=8)
        self.registrar_widget_tema(linha_id, "frame")

        lbl_id = tk.Label(linha_id, text="ID do aluno", font=("Arial", 11, "bold"), bg="#121a2d", width=15, anchor="w", fg="#e2e8f0")
        lbl_id.pack(side="left", padx=(0, 10))
        self.registrar_widget_tema(lbl_id, "label")

        self.id_atualizar = tk.Entry(linha_id, width=20, font=("Arial", 11), bd=1, relief="solid", bg="#0f172a", fg="#f8fafc", insertbackground="white", highlightthickness=1, highlightbackground="#24314d")
        self.id_atualizar.pack(side="left")
        self.registrar_widget_tema(self.id_atualizar, "entry")

        campos = []
        for texto in ["Nova nota 1", "Nova nota 2", "Nova nota 3"]:
            linha = tk.Frame(painel, bg="#121a2d")
            linha.pack(pady=7)
            self.registrar_widget_tema(linha, "frame")

            lbl = tk.Label(linha, text=texto, font=("Arial", 11, "bold"), bg="#121a2d", width=15, anchor="w", fg="#e2e8f0")
            lbl.pack(side="left", padx=(0, 10))
            self.registrar_widget_tema(lbl, "label")

            entry = tk.Entry(linha, width=20, font=("Arial", 11), bd=1, relief="solid", bg="#0f172a", fg="#f8fafc", insertbackground="white", highlightthickness=1, highlightbackground="#24314d")
            entry.pack(side="left")
            self.registrar_widget_tema(entry, "entry")
            campos.append(entry)

        self.notas_atualizar = campos

        btn_atualizar = self.criar_botao_acao(painel, "💾 Atualizar", self.atualizar_notas, "#1f9d55")
        btn_atualizar.pack(pady=(18, 8))
        self.registrar_widget_tema(btn_atualizar, "botao")

        btn_voltar = self.criar_botao_acao(painel, "⬅️ Voltar", lambda: self.mostrar_tela("menu"), "#475569")
        btn_voltar.pack()
        self.registrar_widget_tema(btn_voltar, "botao")

        self.msg_atualizar = tk.Label(painel, text="", font=("Arial", 10, "bold"), bg="#121a2d", fg="#7ef0a6")
        self.msg_atualizar.pack(pady=12)
        self.registrar_widget_tema(self.msg_atualizar, "label")

        return frame

    def criar_frame_remover(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=20, pady=18)
        painel.pack(fill="both", expand=True, padx=180, pady=60)
        self.registrar_widget_tema(painel, "frame")

        titulo = tk.Label(painel, text="🗑️ Remover Aluno", font=("Arial", 24, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(pady=(5, 18))
        self.registrar_widget_tema(titulo, "label")

        linha = tk.Frame(painel, bg="#121a2d")
        linha.pack(pady=10)
        self.registrar_widget_tema(linha, "frame")

        lbl_id = tk.Label(linha, text="ID do aluno", font=("Arial", 11, "bold"), bg="#121a2d", width=15, anchor="w", fg="#e2e8f0")
        lbl_id.pack(side="left", padx=(0, 10))
        self.registrar_widget_tema(lbl_id, "label")

        self.id_remover = tk.Entry(linha, width=20, font=("Arial", 11), bd=1, relief="solid", bg="#0f172a", fg="#f8fafc", insertbackground="white", highlightthickness=1, highlightbackground="#24314d")
        self.id_remover.pack(side="left")
        self.registrar_widget_tema(self.id_remover, "entry")

        btn_remover = self.criar_botao_acao(painel, "🗑️ Remover", self.remover_aluno, "#d93025")
        btn_remover.pack(pady=(15, 10))
        self.registrar_widget_tema(btn_remover, "botao")

        btn_voltar = self.criar_botao_acao(painel, "⬅️ Voltar", lambda: self.mostrar_tela("menu"), "#475569")
        btn_voltar.pack()
        self.registrar_widget_tema(btn_voltar, "botao")

        self.msg_remover = tk.Label(painel, text="", font=("Arial", 10, "bold"), bg="#121a2d", fg="#7ef0a6")
        self.msg_remover.pack(pady=12)
        self.registrar_widget_tema(self.msg_remover, "label")

        return frame

    def criar_frame_relatorio(self):
        frame = tk.Frame(self.root, bg="#0b1020")
        self.registrar_widget_tema(frame, "frame")

        painel = tk.Frame(frame, bg="#121a2d", padx=25, pady=25)
        painel.pack(fill="both", expand=True, padx=200, pady=60)
        self.registrar_widget_tema(painel, "frame")

        titulo = tk.Label(painel, text="📊 Relatório da Turma", font=("Arial", 24, "bold"), bg="#121a2d", fg="#f5f9ff")
        titulo.pack(pady=(5, 20))
        self.registrar_widget_tema(titulo, "label")

        self.relatorio_var = tk.StringVar()
        label = tk.Label(painel, textvariable=self.relatorio_var, font=("Arial", 14), bg="#121a2d", fg="#e5ecff", justify="left")
        label.pack(pady=15)
        self.registrar_widget_tema(label, "label")

        btn_voltar = self.criar_botao_acao(painel, "⬅️ Voltar", lambda: self.mostrar_tela("menu" if self.usuario_logado and self.usuario_logado["tipo"] == "admin" else "menu_funcionario"), "#475569")
        btn_voltar.pack(pady=20)
        self.registrar_widget_tema(btn_voltar, "botao")

        return frame

    def atualizar_lista(self):
        alunos = banco.listar_alunos()
        self.lista_texto.config(state="normal")
        self.lista_texto.delete("1.0", tk.END)

        if not alunos:
            self.lista_texto.insert(tk.END, "Nenhum aluno cadastrado.")
        else:
            for aluno in alunos:
                id_aluno, nome, nota1, nota2, nota3 = aluno
                media = utilidades.calcular_media(nota1, nota2, nota3)
                situacao = utilidades.verificar_situacao(media)
                texto = (
                    f"[{id_aluno}] {nome} | N1: {nota1:.1f} | N2: {nota2:.1f} | N3: {nota3:.1f} | "
                    f"Média: {media:.1f} | {situacao}\n"
                )
                self.lista_texto.insert(tk.END, texto)

        self.lista_texto.config(state="disabled")

    def buscar_por_situacao(self):
        situacao = self.busca_nome.get().strip()
        if not situacao:
            self.resultado_busca.config(state="normal")
            self.resultado_busca.delete("1.0", tk.END)
            self.resultado_busca.insert(tk.END, "Informe uma situação: Aprovado, Recuperação ou Reprovado.")
            self.resultado_busca.config(state="disabled")
            return

        resultados = banco.buscar_aluno_por_situacao(situacao)
        self.resultado_busca.config(state="normal")
        self.resultado_busca.delete("1.0", tk.END)

        if not resultados:
            self.resultado_busca.insert(tk.END, "Nenhum aluno encontrado para essa situação.")
        else:
            for aluno in resultados:
                id_aluno, nome, nota1, nota2, nota3 = aluno
                media = utilidades.calcular_media(nota1, nota2, nota3)
                situacao_aluno = utilidades.verificar_situacao(media)
                linha = (
                    f"[{id_aluno}] {nome} | N1: {nota1:.1f} | N2: {nota2:.1f} | N3: {nota3:.1f} | "
                    f"Média: {media:.1f} | {situacao_aluno}\n"
                )
                self.resultado_busca.insert(tk.END, linha)

        self.resultado_busca.config(state="disabled")

    def buscar_aluno(self):
        nome = self.busca_nome.get().strip()
        resultados = banco.buscar_aluno_por_nome(nome)

        self.resultado_busca.config(state="normal")
        self.resultado_busca.delete("1.0", tk.END)

        if not resultados:
            self.resultado_busca.insert(tk.END, "Nenhum aluno encontrado.")
        else:
            for aluno in resultados:
                id_aluno, nome, nota1, nota2, nota3 = aluno
                media = utilidades.calcular_media(nota1, nota2, nota3)
                situacao = utilidades.verificar_situacao(media)
                linha = (
                    f"[{id_aluno}] {nome} | N1: {nota1:.1f} | N2: {nota2:.1f} | N3: {nota3:.1f} | "
                    f"Média: {media:.1f} | {situacao}\n"
                )
                self.resultado_busca.insert(tk.END, linha)

        self.resultado_busca.config(state="disabled")

    def atualizar_notas(self):
        try:
            id_aluno = int(self.id_atualizar.get())
        except ValueError:
            self.msg_atualizar.config(text="ID inválido.", fg="#fca5a5")
            return

        try:
            notas = [float(campo.get()) for campo in self.notas_atualizar]
        except ValueError:
            self.msg_atualizar.config(text="Use números válidos nas notas.", fg="#fca5a5")
            return

        if any(nota < 0 or nota > 10 for nota in notas):
            self.msg_atualizar.config(text="As notas devem estar entre 0 e 10.", fg="#fca5a5")
            return

        if banco.atualizar_notas(id_aluno, notas[0], notas[1], notas[2]):
            self.msg_atualizar.config(text="Notas atualizadas com sucesso!", fg="#7ef0a6")
        else:
            self.msg_atualizar.config(text="Aluno não encontrado.", fg="#fca5a5")

    def remover_aluno(self):
        try:
            id_aluno = int(self.id_remover.get())
        except ValueError:
            self.msg_remover.config(text="ID inválido.", fg="#fca5a5")
            return

        if banco.remover_aluno(id_aluno):
            self.msg_remover.config(text="Aluno removido com sucesso!", fg="#7ef0a6")
        else:
            self.msg_remover.config(text="Aluno não encontrado.", fg="#fca5a5")

    def salvar_cadastro(self):
        nome = self.campos_cadastro[0].get().strip()
        if not nome:
            self.msg_cadastro.config(text="Nome inválido.", fg="#fca5a5")
            return

        try:
            notas = [float(campo.get()) for campo in self.campos_cadastro[1:4]]
        except ValueError:
            self.msg_cadastro.config(text="Informe apenas números válidos nas notas.", fg="#fca5a5")
            return

        if any(nota < 0 or nota > 10 for nota in notas):
            self.msg_cadastro.config(text="As notas devem estar entre 0 e 10.", fg="#fca5a5")
            return

        banco.cadastrar_aluno(nome, notas[0], notas[1], notas[2])
        self.msg_cadastro.config(text="Aluno cadastrado com sucesso!", fg="#7ef0a6")
        for campo in self.campos_cadastro:
            campo.delete(0, tk.END)

    def abrir_cadastro(self):
        self.mostrar_tela("cadastro")

    def abrir_lista(self):
        self.atualizar_lista()
        self.mostrar_tela("lista")

    def abrir_buscar(self):
        self.mostrar_tela("buscar")

    def abrir_atualizar(self):
        self.mostrar_tela("atualizar")

    def abrir_remover(self):
        self.mostrar_tela("remover")

    def abrir_relatorio(self):
        dados = banco.relatorio_turma()
        texto = (
            f"Total de alunos: {dados['total']}\n"
            f"Aprovados: {dados['aprovados']}\n"
            f"Em recuperação: {dados['recuperacao']}\n"
            f"Reprovados: {dados['reprovados']}\n"
            f"Média da turma: {dados['media_turma']:.1f}\n"
        )
        if dados["melhor_aluno"]:
            texto += f"Melhor aluno: {dados['melhor_aluno']['nome']} (Média: {dados['melhor_aluno']['media']:.1f})\n"
        if dados["pior_aluno"]:
            texto += f"Pior desempenho: {dados['pior_aluno']['nome']} (Média: {dados['pior_aluno']['media']:.1f})\n"
        self.relatorio_var.set(texto)
        self.mostrar_tela("relatorio")

    def abrir_top_3(self):
        ranking = banco.melhores_alunos(3)
        self.resultado_busca.config(state="normal")
        self.resultado_busca.delete("1.0", tk.END)
        if not ranking:
            self.resultado_busca.insert(tk.END, "Nenhum aluno cadastrado.")
        else:
            self.resultado_busca.insert(tk.END, "🏆 Top 3 Melhores Alunos:\n\n")
            for i, aluno in enumerate(ranking, 1):
                self.resultado_busca.insert(
                    tk.END, f"{i}º {aluno['nome']} - Média: {aluno['media']:.1f} ({aluno['situacao']})\n"
                )
        self.resultado_busca.config(state="disabled")
        self.mostrar_tela("buscar")

    def exportar_relatorio(self):
        caminho = banco.exportar_relatorio_txt()
        self.msg_login.config(text=f"Relatório exportado para: {caminho}", fg="#7ef0a6")

    def abrir_menu_por_perfil(self):
        if self.usuario_logado and self.usuario_logado["tipo"] == "admin":
            self.mostrar_tela("menu_admin")
        else:
            self.mostrar_tela("menu_funcionario")

    def sair(self):
        self.usuario_logado = None
        self.atualizar_info_usuario()
        self.mostrar_tela("login")


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    app = SistemaNotasApp(root)
    app.atualizar_info_usuario()
    root.mainloop()