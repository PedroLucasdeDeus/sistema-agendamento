from flask import Blueprint, render_template, request, redirect, url_for, flash

from sqlalchemy.exc import IntegrityError

from models import db, Agendamento, Cliente, Horario

agendamentos_bp = Blueprint('agendamentos', __name__, url_prefix='/agendamentos')


@agendamentos_bp.route('/')
def listar():
    # Join com Horario para ordenar os agendamentos pela data/hora do horário.
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
        flash('Cliente ou horário inválido.', 'error')
        return redirect(url_for('agendamentos.listar'))

    # Verifica manualmente se o horário já tem
    # agendamento ativo, evitando insert desnecessário e permitindo mensagem clara
    ocupado = Agendamento.query.filter_by(horario_id=horario.id).first()
    if ocupado:
        flash('Este horário já está ocupado. Escolha outro.', 'error')
        return redirect(url_for('agendamentos.listar'))

    agendamento = Agendamento(cliente_id=cliente.id, horario_id=horario.id)
    horario.disponivel = False
    db.session.add(agendamento)

    # Em caso de requisições simultâneas, a checagem manual
    # pode falhar, mas o unique do banco garante consistência ao final
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Este horário acabou de ser ocupado. Tente outro.', 'error')
        return redirect(url_for('agendamentos.listar'))

    # Devolve apenas o fragmento da nova linha para o front
    # inserir na tabela sem recarregar a página.
    return render_template('agendamentos/_linha.html', agendamento=agendamento)
