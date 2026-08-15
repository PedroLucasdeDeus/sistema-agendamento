from flask import Blueprint, request, render_template
from extensions import db
import datetime as dt

from models import Horario
from exceptions import DadosHorarioInvalidos, HorarioDuplicado, HorarioNaoEncontrado, DataInvalidaPassado, HoraInvalidaPassado, HorarioAgendado



# ***MÉTODOS DE CONSULTA/PERSISTÊNCIA NO BANCO DE DADOS***
def salvar(horario):
    """Salva no banco"""
    db.session.add(horario)
    db.session.commit()
    return horario


def alterar(horario, data, hora):
    """Altera no banco"""
    horario.data = data
    horario.hora = hora 
    db.session.commit()
    return horario


def listar(disponivel_str=None, data_inicio=None, data_fim=None):
    """Lista registros do banco usando filtros"""
    query = Horario.query

    if disponivel_str is not None:
        esta_disponivel = disponivel_str.lower() == 'true'
        query = query.filter(Horario.disponivel == esta_disponivel)

    if data_inicio:
        query = query.filter(Horario.data >= data_inicio)

    if data_fim:
        query = query.filter(Horario.data <= data_fim)

    return query.order_by(Horario.data).all() 


def buscar_por_id(id):
    """Busca pelo id no banco"""
    return Horario.query.get(id)


def buscar_por_data_hora(data, hora):  
    """Busca por data e hora no banco"""  
    return Horario.query.filter_by(data=data, hora=hora).first()


def excluir(horario):    
    """Exclui no banco"""
    db.session.delete(horario)
    db.session.commit()




# ***MÉTODOS AUXILIARES***
def formatar_data(data):
    """Converte a data do formato string para o formato Date"""
    try:
        f_data = dt.datetime.strptime(data, "%Y-%m-%d").date()         
        return f_data
    
    except TypeError:
        raise DadosHorarioInvalidos("Data faltando!")
    
    except ValueError:
        raise DadosHorarioInvalidos("O formato da data deve ser AAAA-MM-DD, além de ser um data real.") 


def formatar_hora( hora):
    """Converte a hora do formato string para o formato Time"""
    try:        
        f_hora = dt.datetime.strptime(hora, "%H:%M").time()
        return f_hora
    
    except TypeError:
        raise DadosHorarioInvalidos("Hora faltando!")
    
    except ValueError:
        raise DadosHorarioInvalidos("O formato da hora HH:MM, além de ser hora real.") 


def validar_data_hora(data, hora):       
    """Verifica se data/hora são válidas para um agendamento futuro"""    
    if data == None or hora == None:
        raise DadosHorarioInvalidos("Data ou hora faltando!") 
            
    if data < dt.date.today():
        raise DataInvalidaPassado("A data está no passado!")

    if data == dt.date.today() and hora < dt.datetime.now().time():
        raise HoraInvalidaPassado("A hora está no passado!") 


def buscar_horario(id):
    """Busca um horário cadastrado no banco de dados"""
    horario_encontrado = buscar_por_id(id)
    if not horario_encontrado:
        raise HorarioNaoEncontrado("Horário não encontrado!")
    return horario_encontrado


def verificar_duplicidade(data, hora):
    """Verifica se já existe no banco uma combinação de data + hora cadastrada"""
    if buscar_por_data_hora(data, hora):
        raise HorarioDuplicado("Horário já cadastrado no sistema!")


def verificar_agendamento(horario):
    """Verifica se um horário possui agendamento"""
    if not horario.disponivel:
        raise HorarioAgendado("Este horário está agendado!")


def formatar_json(horario):
    """Converte as informações de um horário para o formato json"""
    return {              
        "id": horario.id,
        "data": horario.data.strftime("%Y-%m-%d"),
        "hora": horario.hora.strftime("%H:%M"),
        "disponivel": horario.disponivel        
    }



# ***SERVICES\CASOS DE USO***
def cadastrar_horario(horario_novo):
    """Cadastra um horário no banco validando data/hora e verificando se as informações não estão duplicadas""" 
    data_nova = horario_novo.data
    hora_nova = horario_novo.hora    

    validar_data_hora(data_nova, hora_nova)
    verificar_duplicidade(data_nova, hora_nova)    

    horario_criado = Horario(data_nova, hora_nova)
    return salvar(horario_criado)


def alterar_horario(horario_atualizado, id):   
    """Altera um horário no banco validando data/hora e verificando se as informações não estão duplicadas""" 
    data_atualizada = horario_atualizado.data
    hora_atualizada = horario_atualizado.hora
    validar_data_hora(data_atualizada, hora_atualizada)

    horario_encontrado = buscar_horario(id)  
    verificar_agendamento(horario_encontrado)

    data_encontrada = horario_encontrado.data
    hora_encontrada = horario_encontrado.hora

    if not (data_atualizada == data_encontrada and hora_atualizada == hora_encontrada):
        verificar_duplicidade(data_atualizada, hora_atualizada)
        horario_encontrado = alterar(horario_encontrado, data_atualizada, hora_atualizada)    

    return horario_encontrado


def listar_horarios(disponivel_str=None, data_inicio=None, data_fim=None):
    """Lista os horários do banco filtrando data e disponibilidade"""
    return listar(disponivel_str, data_inicio, data_fim)   


def excluir_horario(id):
    """Exclui um horário do banco de dados se não estiver agendado"""
    horario_encontrado = buscar_horario(id) 
    verificar_agendamento(horario_encontrado)

    excluir(horario_encontrado)

   


# ***ROUTES***
horarios_bp = Blueprint(
    "horarios",
    __name__,
    url_prefix="/horarios"
)


@horarios_bp.route("/pagina", methods=["GET"])
def pagina_horarios():
    return render_template("horarios/horarios.html")


@horarios_bp.route("/", methods=["POST"])
def route_cadastro():
    dados = request.get_json(silent=True)
    if not dados:
        return {
            "erro": "Os dados de horário devem ser enviados em JSON!"
        }, 400

    data = dados.get("data")
    hora = dados.get("hora")

    try:
        data = formatar_data(data)
        hora = formatar_hora(hora)

        horario = Horario(data, hora)
        horario = cadastrar_horario(horario)

    except (
        DadosHorarioInvalidos,
        DataInvalidaPassado,
        HoraInvalidaPassado,
        HorarioDuplicado        
    ) as erro:
        return {
            "erro": str(erro)
        }, 400

    return {
        "mensagem": "Horário cadastrado com sucesso!",
        "horario": formatar_json(horario)
    }, 201

    
@horarios_bp.route("/<int:id>", methods=["PUT"])
def route_alteracao(id):     
    dados = request.get_json(silent=True)
    if not dados:
        return {
            "erro": "Os dados de horário devem ser enviados em JSON!"
        }, 400

    data = dados.get("data")
    hora = dados.get("hora")

    try:
        data = formatar_data(data)
        hora = formatar_hora(hora)

        horario = Horario(data, hora)
        horario = alterar_horario(horario, id)

    except (
        DadosHorarioInvalidos,
        DataInvalidaPassado,
        HoraInvalidaPassado,
        HorarioDuplicado,
        HorarioNaoEncontrado,
        HorarioAgendado
    ) as erro:
        return {
            "erro": str(erro)
        }, 400

    return {
        "mensagem": "Horário alterado com sucesso!",
        "horario": formatar_json(horario)
    }, 200


@horarios_bp.route("/", methods=["GET"])
def route_listagem():
    disponivel_str = request.args.get("disponivel")
    data_inicio_str = request.args.get("data_inicio")
    data_fim_str = request.args.get("data_fim")

    data_inicio = None
    data_fim = None

    try:
        if data_inicio_str:
            data_inicio = formatar_data(data_inicio_str)

        if data_fim_str:
            data_fim = formatar_data(data_fim_str)

    except DadosHorarioInvalidos as erro:
        return {
            "erro": str(erro)
        }, 400

    horarios = listar_horarios(disponivel_str, data_inicio, data_fim)  

    horarios_json = [formatar_json(h) for h in horarios]    
    return {
        "horarios": horarios_json
    }, 200


@horarios_bp.route("/<int:id>", methods=["DELETE"])
def route_exclusao(id):
    try:
        excluir_horario(id)

    except (
        HorarioNaoEncontrado, 
        HorarioAgendado
    ) as erro:
        return {
            "erro": str(erro)
        }, 400
    
    return "", 204


@horarios_bp.route("/<int:id>", methods=["GET"])
def route_busca(id):
    try:
        horario = buscar_horario(id)
    except (
        HorarioNaoEncontrado
    ) as erro:
        return {
            "erro": str(erro)
        }, 400

    return {
        "mensagem": "Horário encontrado com sucesso!",
        "horario": formatar_json(horario)
    }, 200

