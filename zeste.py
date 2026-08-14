import datetime as dt
from models import Horario
from routes.horarios import cadastrar_horario, listar_horarios, alterar_horario, excluir_horario
from app import app




with app.app_context():
    """TESTES"""
    op = 10
    match op:
        case 1:
        # Cadastrar um horário válido:
            dt1 = "01/10/2026"
            hr1 = "22:00"
            h1 = Horario(dt1, hr1)
            cadastrar_horario(h1)

        case 2:
            # Cadastrar horário com valores de dia, mês, ano e hora incorretos:
            dt3 = "32/13/-2025"  # Dia 32, Mês 13, Ano negativo
            hr3 = "25:61"        # Hora 25 e Minuto 61
            h3 = Horario(dt3, hr3)
            cadastrar_horario(h3)

        case 3:
            # Cadastrar horário com data + hora já cadastrados (duplicado):
            dt4 = "25/11/2025"
            hr4 = "22:00"
            h4 = Horario(dt4, hr4)
            cadastrar_horario(h4)

        case 4:
            # Cadastrar horário logicamente errado (data no passado):
            dt5 = "10/05/2026"
            hr5 = "14:00"
            h5 = Horario(dt5, hr5)
            cadastrar_horario(h5)

        case 5:
            # Listando horários cadastrados
            horarios = listar_horarios()
            for h in horarios:
                print(f"Data: {h.data} Hora: {h.hora}")

        case 6:
            # Alterando um horário cadastrado com dados válidos
            dt6 = "10/12/2026"
            hr6 = "15:00"
            id = 2
            h6 = Horario(dt6, hr6)
            alterar_horario(h6, id)

        case 7:
            # Alterando um horário cadastrado com dados inválidos
            dt7 = "45/13/2026"
            hr7 = "45:00"
            id = 2
            h7 = Horario(dt7, hr7)
            alterar_horario(h7, id)

        case 8:
            # Alterando um horário cadastrado com os mesmos dados
            dt8 = "10/12/2026"
            hr8 = "14:00"
            id = 2
            h8 = Horario(dt8, hr8)
            alterar_horario(h8, id)

        case 9:
            # Alterando um horário cadastrado com data e hora duplicadas
            dt9 = "01/10/2026"
            hr9 = "22:00"
            id = 2
            h9 = Horario(dt9, hr9)
            alterar_horario(h9, id)


        case 10:
            # Excluindo um horário sem agendamento       
            id = 1      
            excluir_horario(id)


        case 10:
            # Excluindo um horário com agendamento          
            id = 4        
            excluir_horario(4)

        case _:
            pass
