class DadosHorarioInvalidos(Exception):
    """Erro lançado quando os dados de data e hora de um horário estão incorretos"""
    pass

class DataInvalidaPassado(Exception):
    """Erro lançado quando uma data é anterior à atual"""
    pass

class HoraInvalidaPassado(Exception):
    """Erro lançado quando uma hora é anterior à atual, considerando a data atual"""
    pass

class HorarioAgendado(Exception):
    """Erro lançado ao verificar que um horário já está agendado"""

class HorarioDuplicado(Exception):
    """Erro lançado ao verificar que um horário já está cadastrado no sistema"""

class HorarioNaoEncontrado(Exception):
    """Erro lançao ao não encontrar um horário cadastrado"""