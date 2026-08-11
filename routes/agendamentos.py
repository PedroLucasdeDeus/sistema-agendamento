from flask import Blueprint, render_template, request, redirect, url_for, flash

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models import db, Agendamento, Cliente, Horario

agendamentos_bp = Blueprint('agendamentos', __name__, url_prefix='/agendamentos')


def _resposta_erro(mensagem):
    """Devolve a mensagem de erro no formato certo para quem chamou.

    - Requisição HTMX (formulário e botão via HTMX): fragmento _erro.html
      (um <tr>) para ser inserido no hx-target sem recarregar a página;
    - Requisição comum (sem JS): redirect com flash, como página inteira.
    Assim o erro nunca estoura um 500 e sempre é exibido ao usuário.
    """
    if request.headers.get('HX-Request'):
        return render_template('agendamentos/_erro.html', mensagem=mensagem)
    flash(mensagem, 'error')
    return redirect(url_for('agendamentos.listar'))


@agendamentos_bp.route('/')
def listar():
    # Join com Horario para ordenar os agendamentos pela data/hora do horário.
    # A consulta é protegida por try/except: se o banco falhar, mostramos uma
    # lista vazia com mensagem em vez de deixar um erro 500 estourar.
    try:
        agendamentos = (
            Agendamento.query
            .filter_by(status='ativo')
            .join(Agendamento.horario)
            .order_by(Horario.data, Horario.hora) # Ordena pelos campos data e hora, sujeito a mudanças posteriormente.
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
    cliente_id = request.form.get('cliente_id', type=int)
    horario_id = request.form.get('horario_id', type=int)

    horario = db.session.get(Horario, horario_id)
    cliente = db.session.get(Cliente, cliente_id)

    # IDs precisam existir no banco.
    if not horario or not cliente:
        return _resposta_erro('Cliente ou horário inválido.')

    # O formulário só lista horários disponíveis, mas uma requisição
    # forjada/duplicada pode mandar um horário bloqueado (ex.: marcado como
    # indisponível pelo módulo de Horários). Sem esta checagem, criaríamos
    # uma reserva num horário que deveria estar bloqueado.
    if not horario.disponivel:
        return _resposta_erro('Este horário está indisponível.')

    # Verifica manualmente se o horário já tem agendamento ATIVO.
    # Se existir uma linha CANCELADA, reaproveitamos a MESMA linha
    # (reativação) em vez de inserir: como horario_id é UNIQUE, o banco
    # não permitiria uma segunda linha para o mesmo horário — e sem isso,
    # um horário cancelado nunca mais poderia ser reservado.
    existente = Agendamento.query.filter_by(horario_id=horario.id).first()

    if existente and existente.status == 'ativo':
        return _resposta_erro('Este horário já está ocupado. Escolha outro.')

    if existente:
        existente.cliente_id = cliente.id
        existente.status = 'ativo'
        agendamento = existente
    else:
        agendamento = Agendamento(cliente_id=cliente.id, horario_id=horario.id)
        db.session.add(agendamento)

    horario.disponivel = False

    # Em caso de requisições simultâneas, a checagem manual
    # pode falhar, mas o unique do banco garante consistência ao final.
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _resposta_erro('Este horário acabou de ser ocupado. Tente outro.')
    except SQLAlchemyError:
        # Segunda rede de segurança: qualquer outro erro de banco (tabela
        # inexistente, falha de conexão etc.) vira mensagem amigável em vez
        # de estourar um 500 no navegador do usuário.
        db.session.rollback()
        return _resposta_erro('Não foi possível salvar o agendamento. Tente novamente.')

    # Devolve apenas o fragmento da nova linha para o front
    # inserir na tabela sem recarregar a página.
    return render_template('agendamentos/_linha.html', agendamento=agendamento)


@agendamentos_bp.route('/<int:id>/cancelar', methods=['PATCH'])
def cancelar(id):
    agendamento = db.session.get(Agendamento, id)

    # Só faz sentido cancelar um agendamento que ainda está ativo.
    if not agendamento or agendamento.status != 'ativo':
        return _resposta_erro('Agendamento não encontrado ou já cancelado.')

    # Não apaga o registro (preserva histórico/auditoria) — só
    # muda o status. A listagem filtra status='ativo', então ele some da tela.
    agendamento.status = 'cancelado'
    agendamento.horario.disponivel = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return _resposta_erro('Não foi possível cancelar o agendamento. Tente novamente.')

    # Corpo vazio + hx-swap="outerHTML" no <tr>
    # faz o HTMX substituir a linha por nada, removendo-a do DOM.
    return '', 200
