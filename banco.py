import json
import os
import utilidades

# Caminhos dos arquivos
ARQUIVO_DADOS = os.path.join(os.path.dirname(__file__), "alunos.json")
ARQUIVO_USUARIOS = os.path.join(os.path.dirname(__file__), "usuarios.json")

USUARIOS_PADRAO = [
    {"usuario": "admin", "senha": "admin123", "tipo": "admin"},
    {"usuario": "funcionario", "senha": "func123", "tipo": "funcionario"},
]

def _carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return {"proximo_id": 2, "alunos": [[1, "Maria Silva", 8.0, 7.0, 9.0]]}
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except Exception:
        return {"proximo_id": 2, "alunos": []}

def _salvar_dados(dados):
    # No Vercel, a gravação falha silenciosamente para evitar o Erro 500
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return USUARIOS_PADRAO
    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados if isinstance(dados, list) else USUARIOS_PADRAO
    except Exception:
        return USUARIOS_PADRAO

def autenticar_usuario(usuario, senha):
    usuarios = _carregar_usuarios()
    for conta in usuarios:
        if conta.get("usuario") == usuario and conta.get("senha") == senha:
            return conta
    return None

def listar_alunos():
    dados = _carregar_dados()
    return dados.get("alunos", [])

def cadastrar_aluno(nome, nota1, nota2, nota3):
    dados = _carregar_dados()
    proximo_id = dados.get("proximo_id", 1)
    aluno = [proximo_id, nome.strip(), float(nota1), float(nota2), float(nota3)]
    dados["alunos"].append(aluno)
    dados["proximo_id"] = proximo_id + 1
    _salvar_dados(dados)
    return aluno

def relatorio_turma():
    alunos = listar_alunos()
    if not alunos:
        return {
            "total": 0,
            "aprovados": 0,
            "recuperacao": 0,
            "reprovados": 0,
            "media_turma": 0.0,
        }

    total = len(alunos)
    aprovados = 0
    recuperacao = 0
    reprovados = 0
    soma_medias = 0.0

    for aluno in alunos:
        _, _, nota1, nota2, nota3 = aluno
        media = utilidades.calcular_media(nota1, nota2, nota3)
        soma_medias += media

        if media >= 7:
            aprovados += 1
        elif media >= 4:
            recuperacao += 1
        else:
            reprovados += 1

    return {
        "total": total,
        "aprovados": aprovados,
        "recuperacao": recuperacao,
        "reprovados": reprovados,
        "media_turma": soma_medias / total,
    }