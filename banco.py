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

alunos = []
usuarios = []
logs_acesso = []
_proximo_id = 1


def _carregar_dados():
    global alunos, _proximo_id
    if not os.path.exists(ARQUIVO_DADOS):
        alunos = []
        _proximo_id = 1
        return

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            alunos = dados.get("alunos", [])
            _proximo_id = dados.get("proximo_id", 1)
    except (json.JSONDecodeError, OSError):
        alunos = []
        _proximo_id = 1


def _salvar_dados():
    dados = {
        "proximo_id": _proximo_id,
        "alunos": alunos,
    }
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def _carregar_usuarios():
    global usuarios
    if not os.path.exists(ARQUIVO_USUARIOS):
        usuarios = [usuario.copy() for usuario in USUARIOS_PADRAO]
        _salvar_usuarios()
        return

    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            usuarios = dados if isinstance(dados, list) else []
    except (json.JSONDecodeError, OSError):
        usuarios = [usuario.copy() for usuario in USUARIOS_PADRAO]
        _salvar_usuarios()

    if not usuarios:
        usuarios = [usuario.copy() for usuario in USUARIOS_PADRAO]
        _salvar_usuarios()


def _salvar_usuarios():
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=2)


def _carregar_logs():
    global logs_acesso
    if not os.path.exists(ARQUIVO_LOG_ACESSO):
        logs_acesso = []
        return

    try:
        with open(ARQUIVO_LOG_ACESSO, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            logs_acesso = dados if isinstance(dados, list) else []
    except (json.JSONDecodeError, OSError):
        logs_acesso = []


def _salvar_logs():
    with open(ARQUIVO_LOG_ACESSO, "w", encoding="utf-8") as arquivo:
        json.dump(logs_acesso, arquivo, ensure_ascii=False, indent=2)


_carregar_dados()
_carregar_usuarios()
_carregar_logs()


def _caminhos_chaves_usb():
    """Gera a lista de caminhos onde as chaves USB podem estar localizadas."""
    nome_arquivo_chave = "sistema_chave.key"
    caminhos_verificacao = []

    pasta_projeto = os.path.dirname(__file__)
    caminhos_verificacao.append(os.path.join(pasta_projeto, nome_arquivo_chave))

    if os.name == "nt":
        for letra in range(ord("D"), ord("Z") + 1):
            caminho_drive = f"{chr(letra)}:\\"
            if os.path.exists(caminho_drive):
                caminhos_verificacao.append(os.path.join(caminho_drive, nome_arquivo_chave))
    else:
        caminhos_base = ["/media", "/mnt", "/Volumes"]
        for base in caminhos_base:
            if os.path.exists(base):
                try:
                    for pasta in os.listdir(base):
                        caminhos_verificacao.append(os.path.join(base, pasta, nome_arquivo_chave))
                except Exception:
                    pass

    return caminhos_verificacao


def remover_credencial_pendrive_funcionario():
    """Remove apenas o arquivo de autenticação do funcionário, sem mexer no do admin."""
    token_funcionario = "FUNC_SECRET_KEY_123456"
    caminhos = _caminhos_chaves_usb()

    for caminho_arquivo in caminhos:
        if not os.path.exists(caminho_arquivo):
            continue
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                conteudo = arquivo.read().strip()
            if conteudo == token_funcionario:
                os.remove(caminho_arquivo)
        except Exception:
            pass


def validar_chave_usb(tipo_perfil):
    if tipo_perfil == "funcionario":
        remover_credencial_pendrive_funcionario()
        return True

    token_admin = "ADMIN_SECRET_KEY_987654"
    nome_arquivo_chave = "sistema_chave.key"
    caminhos_verificacao = _caminhos_chaves_usb()

    for caminho_arquivo in caminhos_verificacao:
        if not os.path.exists(caminho_arquivo):
            continue
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if conteudo == token_admin:
                    return True
        except Exception:
            pass

    return False


def cadastrar_aluno(nome, nota1, nota2, nota3):
    global _proximo_id
    aluno = (_proximo_id, nome.strip(), float(nota1), float(nota2), float(nota3))
    alunos.append(aluno)
    _proximo_id += 1
    _salvar_dados()
    return aluno


def listar_alunos():
    return alunos.copy()


def buscar_aluno_por_nome(nome):
    termo = nome.lower().strip()
    return [aluno for aluno in alunos if termo in aluno[1].lower()]


def buscar_aluno_por_situacao(situacao):
    termo = situacao.lower().strip()
    alunos_encontrados = []

    for aluno in alunos:
        _, nome, nota1, nota2, nota3 = aluno
        media = utilidades.calcular_media(nota1, nota2, nota3)
        status = utilidades.verificar_situacao(media)
        if termo == status.lower():
            alunos_encontrados.append(aluno)

    return sorted(alunos_encontrados, key=lambda aluno: aluno[1].lower())


def atualizar_notas(id_aluno, nota1, nota2, nota3):
    for indice, aluno in enumerate(alunos):
        if aluno[0] == id_aluno:
            alunos[indice] = (aluno[0], aluno[1], float(nota1), float(nota2), float(nota3))
            _salvar_dados()
            return True
    return False


def remover_aluno(id_aluno):
    for indice, aluno in enumerate(alunos):
        if aluno[0] == id_aluno:
            del alunos[indice]
            _salvar_dados()
            return True
    return False


def melhores_alunos(limit=3):
    ranking = []
    for aluno in alunos:
        _, nome, nota1, nota2, nota3 = aluno
        media = utilidades.calcular_media(nota1, nota2, nota3)
        ranking.append({
            "id": aluno[0],
            "nome": nome,
            "nota1": nota1,
            "nota2": nota2,
            "nota3": nota3,
            "media": media,
            "situacao": utilidades.verificar_situacao(media),
        })
    ranking.sort(key=lambda item: item["media"], reverse=True)
    return ranking[:limit]


def relatorio_turma():
    if not alunos:
        return {
            "total": 0,
            "aprovados": 0,
            "recuperacao": 0,
            "reprovados": 0,
            "media_turma": 0.0,
            "melhor_aluno": None,
            "pior_aluno": None,
        }

    total = len(alunos)
    aprovados = 0
    recuperacao = 0
    reprovados = 0
    soma_medias = 0.0
    melhor_aluno = None
    pior_aluno = None

    for aluno in alunos:
        _, nome, nota1, nota2, nota3 = aluno
        media = (nota1 + nota2 + nota3) / 3
        soma_medias += media

        if media >= 7:
            aprovados += 1
        elif media >= 4:
            recuperacao += 1
        else:
            reprovados += 1

        aluno_info = {
            "id": aluno[0],
            "nome": nome,
            "media": media,
            "situacao": utilidades.verificar_situacao(media),
        }

        if melhor_aluno is None or media > melhor_aluno["media"]:
            melhor_aluno = aluno_info
        if pior_aluno is None or media < pior_aluno["media"]:
            pior_aluno = aluno_info

    return {
        "total": total,
        "aprovados": aprovados,
        "recuperacao": recuperacao,
        "reprovados": reprovados,
        "media_turma": soma_medias / total,
        "melhor_aluno": melhor_aluno,
        "pior_aluno": pior_aluno,
    }


def exportar_relatorio_txt(caminho_arquivo=None):
    dados = relatorio_turma()
    if caminho_arquivo is None:
        caminho_arquivo = os.path.join(os.path.dirname(__file__), "relatorio_turma.txt")

    linhas = [
        "Relatório da Turma",
        "==================",
        f"Total de alunos: {dados['total']}",
        f"Aprovados: {dados['aprovados']}",
        f"Em recuperação: {dados['recuperacao']}",
        f"Reprovados: {dados['reprovados']}",
        f"Média da turma: {dados['media_turma']:.1f}",
    ]

    if dados["melhor_aluno"]:
        linhas.append(
            f"Melhor aluno: {dados['melhor_aluno']['nome']} | Média: {dados['melhor_aluno']['media']:.1f}"
        )
    else:
        linhas.append("Melhor aluno: nenhum")

    if dados["pior_aluno"]:
        linhas.append(
            f"Pior desempenho: {dados['pior_aluno']['nome']} | Média: {dados['pior_aluno']['media']:.1f}"
        )
    else:
        linhas.append("Pior desempenho: nenhum")

    if alunos:
        linhas.append("\nLista de alunos:")
        for aluno in alunos:
            _, nome, nota1, nota2, nota3 = aluno
            media = utilidades.calcular_media(nota1, nota2, nota3)
            linhas.append(
                f"[{aluno[0]}] {nome} | N1: {nota1:.1f} | N2: {nota2:.1f} | N3: {nota3:.1f} | "
                f"Média: {media:.1f} | {utilidades.verificar_situacao(media)}"
            )

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas))

    return caminho_arquivo


def registrar_log_acesso(usuario, tipo, status):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logs_acesso.append({
        "usuario": usuario,
        "tipo": tipo,
        "status": status,
        "data_hora": agora,
    })
    _salvar_logs()


def listar_logs_acesso():
    return [item.copy() for item in logs_acesso]


def autenticar_usuario(usuario, senha):
    for conta in usuarios:
        if conta.get("usuario") == usuario and conta.get("senha") == senha:
            tipo = conta.get("tipo", "funcionario")
            # Exige que a chave USB física correspondente esteja conectada
            if validar_chave_usb(tipo):
                registrar_log_acesso(usuario, tipo, "sucesso")
                return conta
            else:
                registrar_log_acesso(usuario, tipo, "falha_pendrive")
                return None

    if usuario:
        registrar_log_acesso(usuario, "desconhecido", "falha")
    return None


def adicionar_usuario(usuario, senha, tipo):
    usuario = usuario.strip()
    tipo = tipo.lower().strip()

    if not usuario or not senha:
        return False
    if tipo not in {"admin", "funcionario"}:
        return False
    if any(conta.get("usuario", "").lower() == usuario.lower() for conta in usuarios):
        return False

    usuarios.append({
        "usuario": usuario,
        "senha": senha,
        "tipo": tipo,
    })
    _salvar_usuarios()
    return True


def listar_usuarios():
    return [conta.copy() for conta in usuarios]


def remover_usuario(usuario):
    usuario = usuario.strip()
    for indice, conta in enumerate(usuarios):
        if conta.get("usuario") == usuario:
            del usuarios[indice]
            _salvar_usuarios()
            return True
    return False


def atualizar_usuario(usuario, nova_senha=None, novo_tipo=None):
    usuario = usuario.strip()
    for conta in usuarios:
        if conta.get("usuario") == usuario:
            if nova_senha is not None:
                conta["senha"] = nova_senha.strip()
            if novo_tipo is not None:
                novo_tipo = novo_tipo.lower().strip()
                if novo_tipo in {"admin", "funcionario"}:
                    conta["tipo"] = novo_tipo
            _salvar_usuarios()
            return True
    return False