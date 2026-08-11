import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "chave-secreta-clinica"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "clinica.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False