from flask import Blueprint, request, render_template

from extensions import db
from models import Cliente


clientes_bp = Blueprint(
    "clientes",
    __name__,
    url_prefix="/clientes"
)


# ============================================================
# PÁGINAS HTML
# ============================================================

@clientes_bp.route("/pagina", methods=["GET"])
def pagina_clientes():
    return render_template(
        "clientes/lista.html"
    )


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


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def cliente_para_dict(cliente):
    """
    Converte um objeto Cliente para um dicionário.
    """

    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "telefone": cliente.telefone,
        "email": cliente.email
    }


def validar_dados_cliente(nome, telefone, email):
    """
    Valida os dados recebidos para cadastro ou edição.
    Retorna uma mensagem de erro ou None quando os dados são válidos.
    """

    if not nome:
        return "O nome do cliente é obrigatório."

    if len(nome) < 2:
        return "O nome do cliente deve possuir pelo menos 2 caracteres."

    if len(nome) > 100:
        return "O nome do cliente deve possuir no máximo 100 caracteres."

    if not telefone:
        return "O telefone do cliente é obrigatório."

    if len(telefone) < 8:
        return "Informe um telefone válido."

    if len(telefone) > 20:
        return "O telefone deve possuir no máximo 20 caracteres."

    if email:

        if "@" not in email:
            return "Informe um e-mail válido."

        if "." not in email.split("@")[-1]:
            return "Informe um e-mail válido."

        if len(email) > 120:
            return "O e-mail deve possuir no máximo 120 caracteres."

    return None


# ============================================================
# CRUD DE CLIENTES
# ============================================================

@clientes_bp.route("/", methods=["GET"])
def listar_clientes():

    clientes = Cliente.query.order_by(
        Cliente.nome
    ).all()

    return {
        "clientes": [
            cliente_para_dict(cliente)
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

    nome = str(
        dados.get("nome", "")
    ).strip()

    telefone = str(
        dados.get("telefone", "")
    ).strip()

    email = str(
        dados.get("email", "")
    ).strip()


    # --------------------------------------------------------
    # Validação
    # --------------------------------------------------------

    erro = validar_dados_cliente(
        nome,
        telefone,
        email
    )

    if erro:
        return {
            "erro": erro
        }, 400


    # --------------------------------------------------------
    # Criação
    # --------------------------------------------------------

    cliente = Cliente(
        nome=nome,
        telefone=telefone,
        email=email or None
    )

    try:

        db.session.add(cliente)

        db.session.commit()

    except Exception:

        db.session.rollback()

        return {
            "erro": "Não foi possível cadastrar o cliente."
        }, 500


    return {
        "mensagem": "Cliente cadastrado com sucesso.",
        "cliente": cliente_para_dict(cliente)
    }, 201


@clientes_bp.route("/<int:id>", methods=["GET"])
def buscar_cliente(id):

    cliente = db.get_or_404(
        Cliente,
        id
    )

    return cliente_para_dict(cliente)


@clientes_bp.route("/<int:id>", methods=["PUT"])
def editar_cliente(id):

    cliente = db.get_or_404(
        Cliente,
        id
    )

    dados = request.get_json(silent=True)

    if not dados:
        return {
            "erro": "Nenhum dado foi enviado."
        }, 400


    # --------------------------------------------------------
    # Recupera os valores atuais
    # --------------------------------------------------------

    nome = cliente.nome
    telefone = cliente.telefone
    email = cliente.email


    # --------------------------------------------------------
    # Atualiza apenas os campos enviados
    # --------------------------------------------------------

    if "nome" in dados:

        nome = str(
            dados["nome"]
        ).strip()


    if "telefone" in dados:

        telefone = str(
            dados["telefone"]
        ).strip()


    if "email" in dados:

        email = str(
            dados["email"]
        ).strip()


    # --------------------------------------------------------
    # Validação
    # --------------------------------------------------------

    erro = validar_dados_cliente(
        nome,
        telefone,
        email
    )

    if erro:
        return {
            "erro": erro
        }, 400


    # --------------------------------------------------------
    # Atualização
    # --------------------------------------------------------

    cliente.nome = nome
    cliente.telefone = telefone
    cliente.email = email or None


    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        return {
            "erro": "Não foi possível atualizar o cliente."
        }, 500


    return {
        "mensagem": "Cliente atualizado com sucesso.",
        "cliente": cliente_para_dict(cliente)
    }


@clientes_bp.route("/<int:id>", methods=["DELETE"])
def excluir_cliente(id):

    cliente = db.get_or_404(
        Cliente,
        id
    )

    try:

        db.session.delete(cliente)

        db.session.commit()

    except Exception:

        db.session.rollback()

        return {
            "erro": "Não foi possível excluir o cliente."
        }, 500


    return {
        "mensagem": "Cliente excluído com sucesso."
    }