from flask import Blueprint, request, render_template

from extensions import db
from models import Cliente


clientes_bp = Blueprint(
    "clientes",
    __name__,
    url_prefix="/clientes"
)

@clientes_bp.route("/pagina", methods=["GET"])
def pagina_clientes():
    return render_template("clientes/lista.html")


@clientes_bp.route("/novo", methods=["GET"])
def pagina_novo_cliente():
    return render_template(
        "clientes/formulario.html",
        modo_edicao=False
    )


@clientes_bp.route("/<int:id>/visualizar", methods=["GET"])
def pagina_detalhe_cliente(id):
    return render_template(
        "clientes/detalhe.html",
        cliente_id=id
    )
    
@clientes_bp.route("/<int:id>/editar", methods=["GET"])
def pagina_editar_cliente(id):
    return render_template(
        "clientes/formulario.html",
        cliente_id=id,
        modo_edicao=True
    )


# A partir daqui continuam suas rotas do CRUD

@clientes_bp.route("/", methods=["GET"])
def listar_clientes():

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


@clientes_bp.route("/", methods=["POST"])
def criar_cliente():

    dados = request.get_json(silent=True)

    if not dados:
        return {
            "erro": "Os dados do cliente devem ser enviados em JSON."
        }, 400

    nome = dados.get("nome", "").strip()
    telefone = dados.get("telefone", "").strip()
    email = dados.get("email", "").strip()

    if not nome:
        return {
            "erro": "O nome do cliente é obrigatório."
        }, 400

    if not telefone:
        return {
            "erro": "O telefone do cliente é obrigatório."
        }, 400

    cliente = Cliente(
        nome=nome,
        telefone=telefone,
        email=email or None
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


@clientes_bp.route("/<int:id>", methods=["GET"])
def buscar_cliente(id):

    cliente = db.get_or_404(Cliente, id)

    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "telefone": cliente.telefone,
        "email": cliente.email
    }


@clientes_bp.route("/<int:id>", methods=["PUT"])
def editar_cliente(id):

    cliente = db.get_or_404(Cliente, id)

    dados = request.get_json(silent=True)

    if not dados:
        return {
            "erro": "Nenhum dado foi enviado."
        }, 400

    if "nome" in dados:

        nome = dados["nome"].strip()

        if not nome:
            return {
                "erro": "O nome não pode ficar vazio."
            }, 400

        cliente.nome = nome

    if "telefone" in dados:

        telefone = dados["telefone"].strip()

        if not telefone:
            return {
                "erro": "O telefone não pode ficar vazio."
            }, 400

        cliente.telefone = telefone

    if "email" in dados:

        email = dados["email"]

        cliente.email = (
            email.strip()
            if email
            else None
        )

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


@clientes_bp.route("/<int:id>", methods=["DELETE"])
def excluir_cliente(id):

    cliente = db.get_or_404(Cliente, id)

    db.session.delete(cliente)
    db.session.commit()

    return {
        "mensagem": "Cliente excluído com sucesso."
    }