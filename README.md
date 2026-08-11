# Sistema de Agendamento - Clínica de Estética

## Objetivo

Sistema web desenvolvido para auxiliar no gerenciamento
de uma clínica de estética fictícia.

O sistema permite organizar clientes, horários disponíveis
e agendamentos, reduzindo o risco de conflitos de horário
e facilitando a visualização dos próximos atendimentos.

O sistema é destinado ao uso interno da clínica, não sendo
necessário que os clientes realizem seus próprios agendamentos.

---

## Tecnologias utilizadas

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML
- CSS
- Git e GitHub

---

## Funcionalidades

### Clientes

- Cadastro de clientes;
- Listagem de clientes;
- Consulta de cliente;
- Edição de clientes;
- Exclusão de clientes.

### Horários

- Cadastro de horários disponíveis;
- Listagem de horários;
- Controle de disponibilidade.

### Agendamentos

- Agendamento de um cliente em um horário disponível;
- Cancelamento de agendamento;
- Validação para impedir dois clientes no mesmo horário;
- Listagem dos próximos agendamentos.

---

## Organização do projeto

O projeto utiliza uma arquitetura modular baseada
em Flask Blueprints.

```text
clinica-agendamento/
│
├── app.py
├── config.py
├── extensions.py
├── database.py
├── models.py
│
├── routes/
│   ├── clientes.py
│   ├── horarios.py
│   └── agendamentos.py
│
├── templates/
├── static/
│
├── requirements.txt
├── README.md
└── .gitignore