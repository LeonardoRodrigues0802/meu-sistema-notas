import json
import os
from datetime import datetime
import utilidades

ARQUIVO_DADOS = os.path.join(os.path.dirname(__file__), "alunos.json")
ARQUIVO_USUARIOS = os.path.join(os.path.dirname(__file__), "usuarios.json")
ARQUIVO_LOG_ACESSO = os.path.join(os.path.dirname(__file__), "logs_acesso.json")

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

def _salvar_usuarios(usuarios):
    try:
        with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _carregar_logs():
    if not os.path.exists(ARQUIVO_LOG_ACESSO):
        return []
    try:
        with open(ARQUIVO_LOG_ACESSO, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados if isinstance(dados, list) else []
    except Exception:
        return []

def _salvar_logs(logs):
    try:
        with open(ARQUIVO_LOG_ACESSO, "w", encoding="utf-8") as arquivo:
            json.dump(logs, arquivo, ensure_ascii=False, indent=2)
    except Exception:
        pass

def registrar_log_acesso(usuario, tipo, status):
    logs = _carregar_logs()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logs.append({"usuario": usuario, "tipo": tipo, "status": status, "data_hora": agora})
    _salvar_logs(logs)

def listar_logs_acesso():
    return _carregar_logs()

def autenticar_usuario(usuario, senha):
    usuarios = _carregar_usuarios()
    for conta in usuarios:
        if conta.get("usuario") == usuario and conta.get("senha") == senha:
            tipo = conta.get("tipo", "funcionario")
            registrar_log_acesso(usuario, tipo, "sucesso")
            return conta
    if usuario:
        registrar_log_acesso(usuario, "desconhecido", "falha")
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

def buscar_aluno_por_nome(nome):
    termo = nome.lower().strip()
    return [aluno for aluno in listar_alunos() if termo in aluno[1].lower()]

def buscar_aluno_por_situacao(situacao):
    termo = situacao.lower().strip()
    encontrados = []
    for aluno in listar_alunos():
        _, _, n1, n2, n3 = aluno
        media = utilidades.calcular_media(n1, n2, n3)
        status = utilidades.verificar_situacao(media)
        if termo == status.lower():
            encontrados.append(aluno)
    return sorted(encontrados, key=lambda x: x[1].lower())

def atualizar_notas(id_aluno, nota1, nota2, nota3):
    dados = _carregar_dados()
    atualizado = False
    for i, aluno in enumerate(dados["alunos"]):
        if aluno[0] == int(id_aluno):
            dados["alunos"][i] = [aluno[0], aluno[1], float(nota1), float(nota2), float(nota3)]
            atualizado = True
            break
    if atualizado:
        _salvar_dados(dados)
    return atualizado

def remover_aluno(id_aluno):
    dados = _carregar_dados()
    novos_alunos = [a for a in dados["alunos"] if a[0] != int(id_aluno)]
    if len(novos_alunos) < len(dados["alunos"]):
        dados["alunos"] = novos_alunos
        _salvar_dados(dados)
        return True
    return False

def melhores_alunos(limit=3):
    ranking = []
    for aluno in listar_alunos():
        _, nome, n1, n2, n3 = aluno
        media = utilidades.calcular_media(n1, n2, n3)
        ranking.append({
            "id": aluno[0], "nome": nome, "nota1": n1, "nota2": n2, "nota3": n3,
            "media": media, "situacao": utilidades.verificar_situacao(media)
        })
    ranking.sort(key=lambda x: x["media"], reverse=True)
    return ranking[:limit]

def relatorio_turma():
    alunos = listar_alunos()
    if not alunos:
        return {"total": 0, "aprovados": 0, "recuperacao": 0, "reprovados": 0, "media_turma": 0.0, "melhor_aluno": None, "pior_aluno": None}
    
    total = len(alunos)
    aprovados = 0
    recuperacao = 0
    reprovados = 0
    soma_medias = 0.0
    melhor_aluno = None
    pior_aluno = None

    for aluno in alunos:
        _, nome, n1, n2, n3 = aluno
        media = (n1 + n2 + n3) / 3
        soma_medias += media
        status = utilidades.verificar_situacao(media)

        if media >= 7: aprovados += 1
        elif media >= 4: recuperacao += 1
        else: reprovados += 1

        info = {"nome": nome, "media": media}
        if melhor_aluno is None or media > melhor_aluno["media"]: melhor_aluno = info
        if pior_aluno is None or media < pior_aluno["media"]: pior_aluno = info

    return {
        "total": total, "aprovados": aprovados, "recuperacao": recuperacao, "reprovados": reprovados,
        "media_turma": soma_medias / total, "melhor_aluno": melhor_aluno, "pior_aluno": pior_aluno
    }

def listar_usuarios():
    return _carregar_usuarios()

def adicionar_usuario(usuario, senha, tipo):
    usuarios = _carregar_usuarios()
    usuario, tipo = usuario.strip(), tipo.lower().strip()
    if not usuario or not senha or tipo not in {"admin", "funcionario"}:
        return False
    if any(u["usuario"].lower() == usuario.lower() for u in usuarios):
        return False
    usuarios.append({"usuario": usuario, "senha": senha, "tipo": tipo})
    _salvar_usuarios(usuarios)
    return True

def remover_usuario(usuario):
    usuarios = _carregar_usuarios()
    novos = [u for u in usuarios if u["usuario"] != usuario]
    if len(novos) < len(usuarios):
        _salvar_usuarios(novos)
        return True
    return False