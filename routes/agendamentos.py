from flask import Blueprint, render_template

from models import Agendamento, Horario

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
    return render_template('agendamentos/lista.html', agendamentos=agendamentos)
