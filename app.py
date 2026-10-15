from flask import Flask, render_template, request, redirect, url_for, session
import banco
import utilidades

app = Flask(__name__)
app.secret_key = "chave_secreta_super_segura"

# Inicializa o banco de dados SQL
banco.inicializar_banco(app)

@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        conta = banco.autenticar_usuario(usuario, senha)
        if conta:
            session["usuario"] = conta["usuario"]
            session["tipo"] = conta["tipo"]
            return redirect(url_for("painel"))
        else:
            erro = "Credenciais inválidas."
    return render_template("login.html", erro=erro)

@app.route("/painel")
def painel():
    if "usuario" not in session:
        return redirect(url_for("login"))
    relatorio = banco.relatorio_turma()
    return render_template("painel.html", usuario=session["usuario"], tipo=session["tipo"], relatorio=relatorio)

@app.route("/alunos")
def listar():
    if "usuario" not in session:
        return redirect(url_for("login"))
    lista_bruta = banco.listar_alunos()
    alunos = []
    for a in lista_bruta:
        media = utilidades.calcular_media(a[2], a[3], a[4])
        alunos.append({"id": a[0], "nome": a[1], "nota1": a[2], "nota2": a[3], "nota3": a[4], "media": media, "situacao": utilidades.verificar_situacao(media)})
    return render_template("listar.html", alunos=alunos, tipo=session["tipo"])

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if "usuario" not in session or session["tipo"] != "admin":
        return redirect(url_for("painel"))
    sucesso = False
    if request.method == "POST":
        nome, n1, n2, n3 = request.form.get("nome"), request.form.get("nota1"), request.form.get("nota2"), request.form.get("nota3")
        if nome and n1 and n2 and n3:
            banco.cadastrar_aluno(nome, n1, n2, n3)
            sucesso = True
    return render_template("cadastrar.html", sucesso=sucesso)

@app.route("/atualizar", methods=["GET", "POST"])
def atualizar():
    if "usuario" not in session or session["tipo"] != "admin":
        return redirect(url_for("painel"))
    msg, sucesso = "", False
    if request.method == "POST":
        id_aluno, n1, n2, n3 = request.form.get("id"), request.form.get("nota1"), request.form.get("nota2"), request.form.get("nota3")
        if id_aluno and n1 and n2 and n3:
            if banco.atualizar_notas(id_aluno, n1, n2, n3):
                msg, sucesso = "Notas atualizadas com sucesso!", True
            else:
                msg = "Aluno não encontrado."
    return render_template("atualizar.html", msg=msg, sucesso=sucesso)

@app.route("/remover", methods=["GET", "POST"])
def remover():
    if "usuario" not in session or session["tipo"] != "admin":
        return redirect(url_for("painel"))
    msg, sucesso = "", False
    if request.method == "POST":
        id_aluno = request.form.get("id")
        if id_aluno:
            if banco.remover_aluno(id_aluno):
                msg, sucesso = "Aluno removido com sucesso!", True
            else:
                msg = "Aluno não encontrado."
    return render_template("remover.html", msg=msg, sucesso=sucesso)

@app.route("/buscar", methods=["GET", "POST"])
def buscar():
    if "usuario" not in session:
        return redirect(url_for("login"))
    resultados = []
    termo = ""
    if request.method == "POST":
        termo = request.form.get("termo", "").strip()
        tipo_busca = request.form.get("tipo_busca")
        if tipo_busca == "situacao":
            brutos = banco.buscar_aluno_por_situacao(termo)
        else:
            brutos = banco.buscar_aluno_por_nome(termo)
        
        for a in brutos:
            media = utilidades.calcular_media(a[2], a[3], a[4])
            resultados.append({"id": a[0], "nome": a[1], "nota1": a[2], "nota2": a[3], "nota3": a[4], "media": media, "situacao": utilidades.verificar_situacao(media)})
    return render_template("buscar.html", resultados=resultados, termo=termo)

@app.route("/top3")
def top3():
    if "usuario" not in session:
        return redirect(url_for("login"))
    ranking = banco.melhores_alunos(3)
    return render_template("top3.html", ranking=ranking)

@app.route("/usuarios", methods=["GET", "POST"])
def gerenciar_usuarios():
    if "usuario" not in session or session["tipo"] != "admin":
        return redirect(url_for("painel"))
    msg, sucesso = "", False
    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "cadastrar":
            u, s, t = request.form.get("novo_usuario"), request.form.get("nova_senha"), request.form.get("novo_tipo")
            if banco.adicionar_usuario(u, s, t):
                msg, sucesso = "Usuário cadastrado com sucesso!", True
            else:
                msg = "Erro ao cadastrar (usuário já existe ou campos inválidos)."
        elif acao == "remover":
            u = request.form.get("remover_usuario")
            if u == "admin":
                msg = "Não é permitido remover o administrador principal."
            elif banco.remover_usuario(u):
                msg, sucesso = "Usuário removido!", True
            else:
                msg = "Usuário não encontrado."
    lista_usuarios = banco.listar_usuarios()
    return render_template("usuarios.html", usuarios=lista_usuarios, msg=msg, sucesso=sucesso)

@app.route("/logs")
def logs():
    if "usuario" not in session or session["tipo"] != "admin":
        return redirect(url_for("painel"))
    registros = banco.listar_logs_acesso()
    return render_template("logs.html", registros=registros)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)