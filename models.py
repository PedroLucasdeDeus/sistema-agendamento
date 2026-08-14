from extensions import db
from exceptions import DadosHorarioInvalidos, DataInvalidaPassado, HoraInvalidaPassado, HorarioAgendado
import datetime as dt



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




class Horario(db.Model):
    __tablename__ = "horarios"

    # ATRIBUTOS
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

    agendamento_id = db.Column( # Precisa referenciar a tabela de "agendamentos". IMPLEMENTAR DEPOIS
        db.Integer,
        # db.ForeignKey("agendamentos.id"), DESCOMENTAR DEPOIS
        nullable=True
    )


    # MÉTODOS
    def __init__(self, data, hora): # recebe um objeto do tipo Date e outro do tipo Time, VÁLIDOS!        
        self.data = data
        self.hora = hora             


    def validar_horario(self):       
        if self.data == None or self.hora == None:
            raise DadosHorarioInvalidos("Data ou hora faltando!")
              
        if self.data < dt.date.today():
            raise DataInvalidaPassado("A data está no passado!")

        if self.data == dt.date.today() and self.hora < dt.datetime.now().time():
            raise HoraInvalidaPassado("A hora está no passado!")      


    def verificar_agendamento(self):
        if self.agendamento_id is not None:
            raise HorarioAgendado("Este horário já está agendado!")


    def agendar_horario(self, agendamento_id):
        self.agendamento_id = agendamento_id

