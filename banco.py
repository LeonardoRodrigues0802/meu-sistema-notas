import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import utilidades

db = SQLAlchemy()

class AlunoModel(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nota1 = db.Column(db.Float, nullable=False)
    nota2 = db.Column(db.Float, nullable=False)
    nota3 = db.Column(db.Float, nullable=False)

class UsuarioModel(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)

class LogModel(db.Model):
    __tablename__ = 'logs_acesso'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    data_hora = db.Column(db.String(30), nullable=False)

def inicializar_banco(app):
    # Se houver uma variável de ambiente DATABASE_URL (usada no Vercel/Supabase), usa ela. Senão, usa SQLite local.
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///sistema.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        if not UsuarioModel.query.filter_by(usuario="admin").first():
            db.session.add(UsuarioModel(usuario="admin", senha="admin123", tipo="admin"))
            db.session.add(UsuarioModel(usuario="funcionario", senha="func123", tipo="funcionario"))
            db.session.commit()
        if not AlunoModel.query.first():
            db.session.add(AlunoModel(nome="Maria Silva", nota1=8.0, nota2=7.0, nota3=9.0))
            db.session.commit()

def registrar_log_acesso(usuario, tipo, status):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    novo_log = LogModel(usuario=usuario, tipo=tipo, status=status, data_hora=agora)
    db.session.add(novo_log)
    db.session.commit()

def listar_logs_acesso():
    logs = LogModel.query.order_by(LogModel.id.desc()).all()
    return [{"usuario": l.usuario, "tipo": l.tipo, "status": l.status, "data_hora": l.data_hora} for l in logs]

def autenticar_usuario(usuario, senha):
    conta = UsuarioModel.query.filter_by(usuario=usuario, senha=senha).first()
    if conta:
        registrar_log_acesso(usuario, conta.tipo, "sucesso")
        return {"usuario": conta.usuario, "tipo": conta.tipo}
    if usuario:
        registrar_log_acesso(usuario, "desconhecido", "falha")
    return None

def listar_alunos():
    alunos = AlunoModel.query.all()
    return [[a.id, a.nome, a.nota1, a.nota2, a.nota3] for a in alunos]

def cadastrar_aluno(nome, nota1, nota2, nota3):
    novo = AlunoModel(nome=nome.strip(), nota1=float(nota1), nota2=float(nota2), nota3=float(nota3))
    db.session.add(novo)
    db.session.commit()
    return [novo.id, novo.nome, novo.nota1, novo.nota2, novo.nota3]

def buscar_aluno_por_nome(nome):
    termo = f"%{nome.lower().strip()}%"
    alunos = AlunoModel.query.filter(AlunoModel.nome.ilike(termo)).all()
    return [[a.id, a.nome, a.nota1, a.nota2, a.nota3] for a in alunos]

def buscar_aluno_por_situacao(situacao):
    termo = situacao.lower().strip()
    encontrados = []
    for a in AlunoModel.query.all():
        media = utilidades.calcular_media(a.nota1, a.nota2, a.nota3)
        status = utilidades.verificar_situacao(media)
        if termo == status.lower():
            encontrados.append([a.id, a.nome, a.nota1, a.nota2, a.nota3])
    return sorted(encontrados, key=lambda x: x[1].lower())

def atualizar_notas(id_aluno, nota1, nota2, nota3):
    aluno = AlunoModel.query.get(int(id_aluno))
    if aluno:
        aluno.nota1 = float(nota1)
        aluno.nota2 = float(nota2)
        aluno.nota3 = float(nota3)
        db.session.commit()
        return True
    return False

def remover_aluno(id_aluno):
    aluno = AlunoModel.query.get(int(id_aluno))
    if aluno:
        db.session.delete(aluno)
        db.session.commit()
        return True
    return False

def melhores_alunos(limit=3):
    ranking = []
    for a in AlunoModel.query.all():
        media = utilidades.calcular_media(a.nota1, a.nota2, a.nota3)
        ranking.append({
            "id": a.id, "nome": a.nome, "nota1": a.nota1, "nota2": a.nota2, "nota3": a.nota3,
            "media": media, "situacao": utilidades.verificar_situacao(media)
        })
    ranking.sort(key=lambda x: x["media"], reverse=True)
    return ranking[:limit]

def relatorio_turma():
    alunos = AlunoModel.query.all()
    if not alunos:
        return {"total": 0, "aprovados": 0, "recuperacao": 0, "reprovados": 0, "media_turma": 0.0, "melhor_aluno": None, "pior_aluno": None}
    
    total = len(alunos)
    aprovados = 0
    recuperacao = 0
    reprovados = 0
    soma_medias = 0.0
    melhor_aluno = None
    pior_aluno = None

    for a in alunos:
        media = (a.nota1 + a.nota2 + a.nota3) / 3
        soma_medias += media

        if media >= 7: aprovados += 1
        elif media >= 4: recuperacao += 1
        else: reprovados += 1

        info = {"nome": a.nome, "media": media}
        if melhor_aluno is None or media > melhor_aluno["media"]: melhor_aluno = info
        if pior_aluno is None or media < pior_aluno["media"]: pior_aluno = info

    return {
        "total": total, "aprovados": aprovados, "recuperacao": recuperacao, "reprovados": reprovados,
        "media_turma": soma_medias / total, "melhor_aluno": melhor_aluno, "pior_aluno": pior_aluno
    }

def listar_usuarios():
    usuarios = UsuarioModel.query.all()
    return [{"usuario": u.usuario, "tipo": u.tipo} for u in usuarios]

def adicionar_usuario(usuario, senha, tipo):
    usuario, tipo = usuario.strip(), tipo.lower().strip()
    if not usuario or not senha or tipo not in {"admin", "funcionario"}:
        return False
    if UsuarioModel.query.filter_by(usuario=usuario).first():
        return False
    novo = UsuarioModel(usuario=usuario, senha=senha, tipo=tipo)
    db.session.add(novo)
    db.session.commit()
    return True

def remover_usuario(usuario):
    conta = UsuarioModel.query.filter_by(usuario=usuario).first()
    if conta and conta.usuario != "admin":
        db.session.delete(conta)
        db.session.commit()
        return True
    return False