from flask import Flask, render_template, request, redirect, url_for, session
import banco
import utilidades

app = Flask(__name__)
app.secret_key = "chave_secreta_super_segura"

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
            erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)

@app.route("/painel")
def painel():
    if "usuario" not in session:
        return redirect(url_for("login"))
    try:
        relatorio = banco.relatorio_turma()
    except Exception:
        relatorio = {"total": 0, "aprovados": 0, "recuperacao": 0, "reprovados": 0, "media_turma": 0.0}
    return render_template("painel.html", usuario=session["usuario"], tipo=session["tipo"], relatorio=relatorio)

@app.route("/alunos")
def listar():
    if "usuario" not in session:
        return redirect(url_for("login"))
    try:
        lista_bruta = banco.listar_alunos()
    except Exception:
        lista_bruta = []
        
    alunos = []
    for a in lista_bruta:
        media = utilidades.calcular_media(a[2], a[3], a[4])
        situacao = utilidades.verificar_situacao(media)
        alunos.append({"id": a[0], "nome": a[1], "nota1": a[2], "nota2": a[3], "nota3": a[4], "media": media, "situacao": situacao})
    return render_template("listar.html", alunos=alunos, tipo=session["tipo"])

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if "usuario" not in session or session["tipo"] != "admin":
        return redirect(url_for("painel"))
    
    sucesso = False
    if request.method == "POST":
        nome = request.form.get("nome")
        n1 = request.form.get("nota1")
        n2 = request.form.get("nota2")
        n3 = request.form.get("nota3")
        if nome and n1 and n2 and n3:
            try:
                banco.cadastrar_aluno(nome, n1, n2, n3)
                sucesso = True
            except Exception:
                pass
    return render_template("cadastrar.html", sucesso=sucesso)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)