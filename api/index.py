from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent

DADOS_ALUNOS = {
    "proximo_id": 2,
    "alunos": [
        [1, "Maria Silva", 8.0, 7.0, 9.0]
    ]
}

USUARIOS = [
    {"usuario": "admin", "senha": "admin123", "tipo": "admin"},
    {"usuario": "funcionario", "senha": "func123", "tipo": "funcionario"},
    {"usuario": "teste", "senha": "123", "tipo": "funcionario"}
]

LOGS_ACESSO = [
    {
        "usuario": "admin",
        "tipo": "admin",
        "status": "sucesso",
        "data_hora": "15/10/2026 15:27:43"
    }
]

def calcular_media(n1, n2, n3):
    return (float(n1) + float(n2) + float(n3)) / 3

def validar_chave_usb(tipo_perfil):
    """Valida a chave do pendrive (simulada ou física) dependendo do perfil."""
    nome_arquivo_chave = "sistema_chave.key"
    token_admin = "ADMIN_SECRET_KEY_987654"

    if tipo_perfil == "funcionario":
        return True

    caminhos_verificacao = []
    caminhos_verificacao.append(BASE_DIR / nome_arquivo_chave)

    if os.name == "nt":
        for letra in range(ord("D"), ord("Z") + 1):
            caminho_drive = Path(f"{chr(letra)}:/")
            if caminho_drive.exists():
                caminhos_verificacao.append(caminho_drive / nome_arquivo_chave)
    else:
        for base in ["/media", "/mnt", "/Volumes"]:
            base_path = Path(base)
            if base_path.exists():
                for pasta in base_path.iterdir():
                    caminhos_verificacao.append(pasta / nome_arquivo_chave)

    for caminho in caminhos_verificacao:
        try:
            if caminho.exists():
                conteudo = caminho.read_text(encoding="utf-8").strip()
                if conteudo == token_admin:
                    return True
        except Exception:
            pass

    return False

@app.route('/api/alunos', methods=['GET'])
def get_alunos():
    return jsonify(DADOS_ALUNOS.get("alunos", []))

@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    return jsonify(USUARIOS)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(LOGS_ACESSO)

@app.route('/api/relatorio', methods=['GET'])
def get_relatorio():
    alunos = DADOS_ALUNOS.get("alunos", [])
    if not alunos:
        return jsonify({
            "total": 0, "aprovados": 0, "recuperacao": 0,
            "reprovados": 0, "media_turma": 0, "melhor_aluno": None, "pior_aluno": None
        })

    aprovados = recuperacao = reprovados = 0
    total_media = 0
    melhor = None
    pior = None

    for aluno in alunos:
        _, nome, nota1, nota2, nota3 = aluno
        media = calcular_media(nota1, nota2, nota3)
        total_media += media

        if media >= 7:
            aprovados += 1
        elif media >= 4:
            recuperacao += 1
        else:
            reprovados += 1

        info = {"nome": nome, "media": media}
        if melhor is None or media > melhor["media"]:
            melhor = info
        if pior is None or media < pior["media"]:
            pior = info

    return jsonify({
        "total": len(alunos),
        "aprovados": aprovados,
        "recuperacao": recuperacao,
        "reprovados": reprovados,
        "media_turma": total_media / len(alunos),
        "melhor_aluno": melhor,
        "pior_aluno": pior
    })

@app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json() or {}
    usuario = (dados.get("usuario") or "").strip()
    senha = (dados.get("senha") or "").strip()

    conta = next((u for u in USUARIOS if u.get("usuario") == usuario and u.get("senha") == senha), None)

    if conta:
        tipo = conta.get("tipo", "funcionario")
        if not validar_chave_usb(tipo):
            return jsonify({"ok": False, "message": "Chave USB do Administrador ausente ou inválida!"}), 403
            
        return jsonify({"ok": True, "usuario": conta})
        
    return jsonify({"ok": False, "message": "Credenciais inválidas"}), 401

@app.route('/api/usuarios/add', methods=['POST'])
def add_usuario():
    dados = request.get_json() or {}
    usuario = (dados.get("usuario") or "").strip()
    senha = (dados.get("senha") or "").strip()
    tipo = (dados.get("tipo") or "funcionario").strip().lower()

    if not usuario or not senha or tipo not in {"admin", "funcionario"}:
        return jsonify({"ok": False, "message": "Dados inválidos"}), 400

    if any(u.get("usuario", "").lower() == usuario.lower() for u in USUARIOS):
        return jsonify({"ok": False, "message": "Usuário já existe"}), 409

    nova_conta = {"usuario": usuario, "senha": senha, "tipo": tipo}
    USUARIOS.append(nova_conta)
    return jsonify({"ok": True, "usuario": nova_conta})

@app.route('/api/alunos/add', methods=['POST'])
def add_aluno():
    dados = request.get_json() or {}
    nome = (dados.get("nome") or "").strip()
    n1, n2, n3 = dados.get("nota1"), dados.get("nota2"), dados.get("nota3")

    if not nome or n1 is None or n2 is None or n3 is None:
        return jsonify({"ok": False, "message": "Dados inválidos"}), 400

    pid = DADOS_ALUNOS["proximo_id"]
    DADOS_ALUNOS["alunos"].append([pid, nome, float(n1), float(n2), float(n3)])
    DADOS_ALUNOS["proximo_id"] += 1
    return jsonify({"ok": True, "id": pid})