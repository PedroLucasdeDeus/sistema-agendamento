from flask import Blueprint, request, render_template, redirect, url_for
from models import Horario
from extensions import db
import datetime as dt
from exceptions import DadosHorarioInvalidos, HorarioDuplicado, HorarioNaoEncontrado, DataInvalidaPassado, HoraInvalidaPassado, HorarioAgendado




# ***MÉTODOS DE CONSULTA/PERSISTÊNCIA NO BANCO***
def salvar(horario):
    db.session.add(horario)
    db.session.commit()
    return horario


def buscar_por_id(id):
    return Horario.query.get(id)


def buscar_por_data_hora(data, hora):    
    return Horario.query.filter_by(data=data, hora=hora).first()


def excluir(horario):    
    db.session.delete(horario)
    db.session.commit()


def alterar(horario, data, hora):
    horario.data = data
    horario.hora = hora 
    db.session.commit()


def listar():
    return Horario.query.all() # Pode ordenar por alguns campos depois





# ***MÉTODOS AUXILIARES***
def formatar_data_hora(data, hora):
    try:
        f_data = dt.datetime.strptime(data, "%Y-%m-%d").date()
        f_hora = dt.datetime.strptime(hora, "%H:%M").time()
        return f_data, f_hora
    
    except TypeError:
        raise DadosHorarioInvalidos("As informações não podem ficar em branco!")
    
    except ValueError:
        raise DadosHorarioInvalidos("O formato da data deve ser DD/MM/AAAA e a hora HH:MM, além de serem datas e horas reais.") 


def buscar_horario(id):
    horario_encontrado = buscar_por_id(id)
    if not horario_encontrado:
        raise HorarioNaoEncontrado("Horário não encontrado!")
    return horario_encontrado


def verificar_duplicidade(data, hora):
    if buscar_por_data_hora(data, hora):
        raise HorarioDuplicado("Horário já cadastrado no sistema!")





# ***SERVICES\CASOS DE USO***
def cadastrar_horario(horario_novo):
    data_nova = horario_novo.data
    hora_nova = horario_novo.hora    

    verificar_duplicidade(data_nova, hora_nova)    
    horario_criado = Horario(data_nova, hora_nova)
    horario_criado.validar_horario()

    return salvar(horario_criado)


def listar_horarios(): # Adicionar filtros no futuro
    return listar()


def alterar_horario(horario_atualizado, id):    
    data_atualizada = horario_atualizado.data
    hora_atualizada = horario_atualizado.hora

    aux = Horario(data_atualizada, hora_atualizada)
    aux.validar_horario()

    horario_encontrado = buscar_horario(id)  
    data_encontrada = horario_encontrado.data
    hora_encontrada = horario_encontrado.hora

    if not (data_atualizada == data_encontrada and hora_atualizada == hora_encontrada):
        verificar_duplicidade(data_atualizada, hora_atualizada)
        alterar(horario_encontrado, data_atualizada, hora_atualizada)    

    return horario_encontrado
    


def excluir_horario(id):
    horario_encontrado = buscar_horario(id) 
    horario_encontrado.verificar_agendamento()

    excluir(horario_encontrado)


def agendar_horario(horario_id, agendamento_id):
    # VERIFICAR SE NÃO TEM AGENDAMENTO_ID 
    horario = buscar_horario(horario_id)
    horario.verificar_agendamento()
    horario.agendar_horario(agendamento_id)

    return horario
    
    

    

# ***ROUTES***
horarios_bp = Blueprint(
    "horarios",
    __name__,
    url_prefix="/horarios"
)

@horarios_bp.route("/", methods=["POST"])
def route_cadastrar_horario():
    data = request.form.get("data")
    hora = request.form.get("hora")

    try:
        data, hora = formatar_data_hora(data, hora)

        horario = Horario(data, hora)
        cadastrar_horario(horario)

    except (
        DadosHorarioInvalidos,
        DataInvalidaPassado,
        HoraInvalidaPassado,
        HorarioDuplicado
    ) as erro:
        return render_template(
            "horarios/horarios.html",
            horarios=listar_horarios(),
            erro=str(erro)
        ), 400

    return redirect(url_for("horarios.route_listar_horarios"))    

    


@horarios_bp.route("/", methods=["GET"])
def route_listar_horarios():
    horarios = listar_horarios()
    return render_template("horarios/horarios.html", horarios=horarios)


@horarios_bp.route("/<int:id>", methods=["PUT"])
def route_alterar_horario(id):     
    data = request.form.get("data")
    hora = request.form.get("hora")

    try:
        data, hora = formatar_data_hora(data, hora)

        horario = Horario(data, hora)

        alterar_horario(horario, id)

    except (
        DadosHorarioInvalidos,
        DataInvalidaPassado,
        HoraInvalidaPassado,
        HorarioDuplicado,
        HorarioNaoEncontrado
    ) as erro:

        return render_template(
            "horarios/horarios.html",
            horarios=listar_horarios(),
            erro=str(erro)
        ), 400

    #return redirect(url_for("horarios.route_listar_horarios")) ESTAVA DANDO ERRO NO SITE
    return "", 200
    
   



@horarios_bp.route("/<int:id>", methods=["DELETE"])
def route_excluir_horario(id):
    try:
        excluir_horario(id)

    except (HorarioNaoEncontrado, HorarioAgendado) as erro:

        return render_template(
            "horarios/horarios.html",
            horarios=listar_horarios(),
            erro=str(erro)
        ), 400

    #return redirect(url_for("horarios.route_listar_horarios")) ESTAVA DANDO ERRO NO SITE
    return "", 200







