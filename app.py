from flask import Flask

from config import Config
from extensions import db
from database import init_db

from routes.clientes import clientes_bp


def create_app():

    app = Flask(__name__)

    # Carrega configurações
    app.config.from_object(Config)

    # Inicializa banco
    db.init_app(app)

    # Registra rotas de clientes
    app.register_blueprint(clientes_bp)

    # Cria banco/tabelas
    init_db(app)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)