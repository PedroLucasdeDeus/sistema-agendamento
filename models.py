from datetime import datetime

from extensions import db


class Cliente(db.Model):

    __tablename__ = "clientes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    cpf = db.Column(
        db.String(14),
        nullable=False,
        unique=True
    )

    telefone = db.Column(
        db.String(20),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=True
    )

    def __repr__(self):

        return f"<Cliente {self.nome}>"


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


class Horario(db.Model):
    __tablename__ = "horarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    data = db.Column(
        db.Date,
        nullable=False
    )

    hora = db.Column(
        db.Time,
        nullable=False
    )

    disponivel = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    def __init__(self, data, hora):     
        self.data = data
        self.hora = hora  
        self.disponivel = True           


 
    



