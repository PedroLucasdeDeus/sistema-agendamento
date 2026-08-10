from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # Temporário, remover posteriormente

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    # Unique garante no bd que um horario só tenha um agendamento.
    horario_id = db.Column(db.Integer, db.ForeignKey('horarios.id'), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default='ativo')
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    cliente = db.relationship('Cliente', backref=db.backref('agendamentos', lazy=True))
    horario = db.relationship('Horario', backref=db.backref('agendamentos', lazy=True))