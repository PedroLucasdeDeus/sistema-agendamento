from datetime import datetime

from extensions import db


class Agendamento(db.Model):

    __tablename__ = "agendamentos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )

    # UNIQUE garante no banco que um horário só tenha um agendamento —
    # é a 2ª camada de defesa contra reservas duplicadas.
    horario_id = db.Column(
        db.Integer,
        db.ForeignKey("horarios.id"),
        nullable=False,
        unique=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ativo"  # 'ativo' | 'cancelado' (soft delete)
    )

    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    cliente = db.relationship(
        "Cliente",
        backref=db.backref("agendamentos", lazy=True)
    )

    horario = db.relationship(
        "Horario",
        backref=db.backref("agendamentos", lazy=True)
    )
