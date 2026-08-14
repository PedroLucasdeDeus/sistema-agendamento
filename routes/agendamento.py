from flask import Blueprint, render_template, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from extensions import db
from models import Agendamento, Cliente, Horario


agendamentos_bp = Blueprint(
    "agendamentos",
    __name__,
    url_prefix="/agendamentos"
)


# ============================================================
# PÁGINA HTML
# ============================================================

@agendamentos_bp.route("/pagina", methods=["GET"])
def pagina_agendamentos():
    return render_template(
        "agendamentos/lista.html"
    )


def _serializar(agendamento):
    """Converte um Agendamento em dict para facilitar o uso com json."""
    return {
        "id": agendamento.id,
        "status": agendamento.status,
        "cliente": {
            "id": agendamento.cliente.id,
            "nome": agendamento.cliente.nome
        },
        "horario": {
            "id": agendamento.horario.id,
            "data": agendamento.horario.data.isoformat(),
            "hora": agendamento.horario.hora.isoformat()
        }
    }


# LISTAR AGENDAMENTOS
@agendamentos_bp.route("/", methods=["GET"])
def listar_agendamentos():
    # Join com Horario para ordenar pela data/hora do horário.
    try:
        agendamentos = (
            Agendamento.query
            .filter_by(status="ativo")
            .join(Agendamento.horario)
            .order_by(Horario.data, Horario.hora)
            .all()
        )
    except SQLAlchemyError:
        db.session.rollback()
        return {"erro": "Não foi possível consultar os agendamentos."}, 500

    return {
        "agendamentos": [
            _serializar(agendamento)
            for agendamento in agendamentos
        ]
    }


# CRIAR AGENDAMENTO
@agendamentos_bp.route("/", methods=["POST"])
def criar_agendamento():
    dados = request.get_json(silent=True)

    if not dados:
        return {
            "erro": "Os dados do agendamento devem ser enviados em JSON."
        }, 400

    cliente_id = dados.get("cliente_id")
    horario_id = dados.get("horario_id")

    if not cliente_id or not horario_id:
        return {
            "erro": "cliente_id e horario_id são obrigatórios."
        }, 400

    cliente = db.session.get(Cliente, cliente_id)
    horario = db.session.get(Horario, horario_id)

    # IDs precisam existir no banco.
    if not cliente or not horario:
        return {"erro": "Cliente ou horário inválido."}, 404

    # O frontend já filtra horários disponíveis, mas uma requisição
    # forjada pode mandar um horário bloqueado pelo módulo de Horários.
    if not horario.disponivel:
        return {"erro": "Este horário está indisponível."}, 409

    # se já existe agendamento ativo para o horário, recusamos com mensagem
    # clara. Se existe uma linha cancelada, reativamos a mesma linha: como
    # horario_id é unique, o banco não aceitaria uma segunda linha — sem a
    # reativação, um horário cancelado nunca mais poderia ser reservado.
    existente = Agendamento.query.filter_by(horario_id=horario.id).first()

    if existente and existente.status == "ativo":
        return {"erro": "Este horário já está ocupado."}, 409

    if existente:
        existente.cliente_id = cliente.id
        existente.status = "ativo"
        agendamento = existente
    else:
        agendamento = Agendamento(cliente_id=cliente.id, horario_id=horario.id)
        db.session.add(agendamento)

    horario.disponivel = False

    # entre a checagem manual e o commit pode haver requisições simultâneas;
    # a constraint do banco grava apenas uma, e a falha da outra vira
    # mensagem amigável em vez de um 500.
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"erro": "Este horário acabou de ser ocupado. Tente outro."}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {"erro": "Não foi possível salvar o agendamento."}, 500

    return {
        "mensagem": "Agendamento criado com sucesso.",
        "agendamento": _serializar(agendamento)
    }, 201


# Cancelar agendamento 
@agendamentos_bp.route("/<int:id>/cancelar", methods=["PATCH"])
def cancelar_agendamento(id):
    agendamento = db.session.get(Agendamento, id)

    # Só é possível cancelar um agendamento que ainda está ativo.
    if not agendamento or agendamento.status != "ativo":
        return {"erro": "Agendamento não encontrado ou já cancelado."}, 404

    # a linha não é apagada (preserva histórico/auditoria),
    # só muda o status — a listagem filtra status='ativo'. O horário volta
    # a ficar disponível para um novo agendamento.
    agendamento.status = "cancelado"
    agendamento.horario.disponivel = True

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return {"erro": "Não foi possível cancelar o agendamento."}, 500

    return {"mensagem": "Agendamento cancelado com sucesso."}
