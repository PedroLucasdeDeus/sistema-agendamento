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