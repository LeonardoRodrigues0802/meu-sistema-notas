from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

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

CODIGOS_WHATSAPP = {}

def calcular_media(n1, n2, n3):
    return (float(n1) + float(n2) + float(n3)) / 3

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
    whatsapp_informado = (dados.get("whatsapp") or "").strip()
    codigo_informado = (dados.get("codigo") or "").strip()

    conta = next((u for u in USUARIOS if u.get("usuario") == usuario and u.get("senha") == senha), None)

    if not conta:
        return jsonify({"ok": False, "message": "Credenciais inválidas"}), 401

    tipo = conta.get("tipo", "funcionario")

    if tipo == "admin":
        if not whatsapp_informado:
            return jsonify({"ok": False, "precisa_whatsapp": True, "message": "Informe o número de WhatsApp para receber o código."}), 200

        if not codigo_informado:
            codigo_gerado = str(random.randint(100000, 999999))
            CODIGOS_WHATSAPP[usuario] = codigo_gerado
            
            print(f"[WHATSAPP SIMULADO para {whatsapp_informado}]: Seu código de acesso é {codigo_gerado}")
            
            return jsonify({
                "ok": False, 
                "precisa_codigo": True, 
                "message": f"Código enviado para {whatsapp_informado}! (Código de teste: {codigo_gerado})"
            }), 200
        
        if CODIGOS_WHATSAPP.get(usuario) != codigo_informado:
            return jsonify({"ok": False, "message": "Código do WhatsApp incorreto ou expirado!"}), 403
        
        CODIGOS_WHATSAPP.pop(usuario, None)

    return jsonify({"ok": True, "usuario": conta})

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