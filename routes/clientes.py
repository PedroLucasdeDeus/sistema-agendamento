from flask import (
    Blueprint,
    request,
    redirect,
    url_for
)

from extensions import db
from models import Cliente


clientes_bp = Blueprint(
    "clientes",
    __name__,
    url_prefix="/clientes"
)


# LISTAR CLIENTES
@clientes_bp.route("/")
def lista():

    clientes = Cliente.query.order_by(
        Cliente.nome
    ).all()

    return {
        "clientes": [
            {
                "id": cliente.id,
                "nome": cliente.nome,
                "telefone": cliente.telefone,
                "email": cliente.email
            }
            for cliente in clientes
        ]
    }


# CADASTRAR CLIENTE
@clientes_bp.route("/novo", methods=["POST"])
def novo():

    dados = request.get_json()

    nome = dados.get("nome")
    telefone = dados.get("telefone")
    email = dados.get("email")

    if not nome:
        return {
            "erro": "O nome é obrigatório."
        }, 400

    if not telefone:
        return {
            "erro": "O telefone é obrigatório."
        }, 400

    cliente = Cliente(
        nome=nome,
        telefone=telefone,
        email=email
    )

    db.session.add(cliente)
    db.session.commit()

    return {
        "mensagem": "Cliente cadastrado com sucesso.",
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone,
            "email": cliente.email
        }
    }, 201


# BUSCAR UM CLIENTE
@clientes_bp.route("/<int:id>")
def buscar(id):

    cliente = db.get_or_404(Cliente, id)

    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "telefone": cliente.telefone,
        "email": cliente.email
    }


# EDITAR CLIENTE
@clientes_bp.route("/<int:id>", methods=["PUT"])
def editar(id):

    cliente = db.get_or_404(Cliente, id)

    dados = request.get_json()

    nome = dados.get("nome")
    telefone = dados.get("telefone")
    email = dados.get("email")

    if nome:
        cliente.nome = nome

    if telefone:
        cliente.telefone = telefone

    if email is not None:
        cliente.email = email

    db.session.commit()

    return {
        "mensagem": "Cliente atualizado com sucesso.",
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone,
            "email": cliente.email
        }
    }


# EXCLUIR CLIENTE
@clientes_bp.route("/<int:id>", methods=["DELETE"])
def excluir(id):

    cliente = db.get_or_404(Cliente, id)

    db.session.delete(cliente)
    db.session.commit()

    return {
        "mensagem": "Cliente excluído com sucesso."
    }