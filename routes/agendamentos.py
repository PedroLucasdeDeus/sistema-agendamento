from flask import Blueprint, render_template, request, redirect, url_for, flash

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models import db, Agendamento, Cliente, Horario

agendamentos_bp = Blueprint('agendamentos', __name__, url_prefix='/agendamentos')


def erro_htmx(mensagem):
    """
    Padroniza erros de rotas HTMX como fragmento HTML, usando HX-Retarget/
    HX-Reswap para renderizar a mensagem em #form-erro em vez do alvo original do form.
    """
    response = render_template('agendamentos/_erro.html', mensagem=mensagem)
    headers = {
        'HX-Retarget': '#form-erro',
        'HX-Reswap': 'innerHTML',
    }
    return response, 200, headers


@agendamentos_bp.route('/')
def listar():
    # Join com Horario para ordenar os agendamentos pela data/hora do horário.
    # Esta rota é acessada via navegação normal (não HTMX), então erro aqui
    # usa flash + render da página inteira mesmo, não fragmento.
    try:
        agendamentos = (
            Agendamento.query
            .filter_by(status='ativo')
            .join(Agendamento.horario)
            .order_by(Horario.data, Horario.hora)  # Sujeito a mudanças posteriormente.
            .all()
        )
        # Dados do formulário de criação: clientes cadastrados e horários livres.
        clientes = Cliente.query.order_by(Cliente.nome).all()
        horarios_disponiveis = Horario.query.filter_by(disponivel=True).all()
    except SQLAlchemyError:
        db.session.rollback()
        agendamentos = []
        clientes = []
        horarios_disponiveis = []
        flash('Erro ao carregar os dados. Tente novamente.', 'error')

    return render_template(
        'agendamentos/lista.html',
        agendamentos=agendamentos,
        clientes=clientes,
        horarios_disponiveis=horarios_disponiveis,
    )


@agendamentos_bp.route('/', methods=['POST'])
def criar():
    cliente_id = request.form.get('cliente_id')
    horario_id = request.form.get('horario_id')

    horario = db.session.get(Horario, horario_id)
    cliente = db.session.get(Cliente, cliente_id)

    # IDs precisam existir no banco.
    if not horario or not cliente:
        return erro_htmx('Cliente ou horário inválido.')

    # O formulário só lista horários disponíveis, mas uma requisição
    # forjada/duplicada pode mandar um horário já bloqueado.
    if not horario.disponivel:
        return erro_htmx('Este horário está indisponível.')

    # Verifica manualmente se o horário já tem agendamento ativo, evitando
    # insert desnecessário e permitindo mensagem clara.
    ocupado = Agendamento.query.filter_by(horario_id=horario.id).first()
    if ocupado:
        return erro_htmx('Este horário já está ocupado. Escolha outro.')

    agendamento = Agendamento(cliente_id=cliente.id, horario_id=horario.id)
    horario.disponivel = False
    db.session.add(agendamento)

    # Em caso de requisições simultâneas, a checagem manual pode falhar,
    # mas o unique do banco garante consistência ao final.
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return erro_htmx('Este horário acabou de ser ocupado. Tente outro.')
    except SQLAlchemyError:
        db.session.rollback()
        return erro_htmx('Não foi possível salvar o agendamento. Tente novamente.')

    # Devolve apenas o fragmento da nova linha, que o HTMX insere
    # no target original do form (#lista-agendamentos), sem recarregar nada.
    return render_template('agendamentos/_linha.html', agendamento=agendamento)


@agendamentos_bp.route('/<int:id>/cancelar', methods=['PATCH'])
def cancelar(id):
    agendamento = db.session.get(Agendamento, id)
    if not agendamento:
        return erro_htmx('Agendamento não encontrado.')

    # Não apaga o registro (preserva histórico/auditoria) — só muda o
    # status. A listagem filtra status='ativo', então ele some da tela.
    agendamento.status = 'cancelado'
    agendamento.horario.disponivel = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return erro_htmx('Não foi possível cancelar o agendamento. Tente novamente.')

    # Corpo vazio + hx-swap="outerHTML" no <tr> (configurado no
    # botão) faz o HTMX remover a linha do DOM.
    return '', 200