from flask import Flask, app, render_template

from config import Config
from extensions import db
from database import init_db

from routes.clientes import clientes_bp
#from routes.horarios import horarios_bp
#from routes.agendamento import agendamentos_bp


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(clientes_bp)
    #app.register_blueprint(horarios_bp)
    app.register_blueprint(agendamentos_bp)

    init_db(app)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)