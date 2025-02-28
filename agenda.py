from flask import Flask, render_template, request, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials
import os
import json

# Definir os escopos de acesso ao Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Carregar as credenciais
creds_json = os.getenv("GOOGLE_CREDENTIALS")
creds_dict = json.loads(creds_json)
credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

gc = gspread.authorize(credentials)
spreadsheet = gc.open("Agenda Site")  # Nome da sua planilha

# Criar o app Flask
app = Flask(__name__)

# Função para carregar as agendas da planilha
def carregar_agendas():
    sheet = spreadsheet.get_worksheet(0)  # Acessa a primeira aba
    agendas_data = sheet.get_all_records()  # Pega todos os dados

    agendas = []
    for agenda in agendas_data:
        agendas.append({
            'id': agenda['ID'],
            'nome': agenda['Nome'],
            'descricao': agenda['Descricao'],
            'dias': agenda['Dias'].split(','),
            'status': agenda['Status'],
            'tarefas': {},
        })

    return agendas

# Função para criar uma nova agenda
def criar_agenda(nome, descricao, dias):
    sheet = spreadsheet.get_worksheet(0)  # Acessa a primeira aba
    dias_string = ",".join(dias)  # Converte lista de dias para uma string
    # Adiciona uma nova linha com os dados da nova agenda
    sheet.append_row([nome, descricao, dias_string, 'Ativa'])  # 'Ativa' como status inicial

# Função para excluir uma agenda da planilha
def excluir_agenda(agenda_id):
    sheet = spreadsheet.get_worksheet(0)  # Acessa a primeira aba
    agenda_row = sheet.find(str(agenda_id))  # Encontra a linha pelo ID da agenda
    if agenda_row:
        sheet.delete_row(agenda_row.row)  # Exclui a linha com esse ID

# Função para editar uma agenda na planilha
def editar_agenda(agenda_id, nome, descricao, dias):
    sheet = spreadsheet.get_worksheet(0)
    agenda_row = sheet.find(str(agenda_id))  # Encontra a linha pela ID
    if agenda_row:
        dias_string = ",".join(dias)
        sheet.update_cell(agenda_row.row, 2, nome)  # Atualiza nome
        sheet.update_cell(agenda_row.row, 3, descricao)  # Atualiza descrição
        sheet.update_cell(agenda_row.row, 4, dias_string)  # Atualiza dias

# Função para arquivar uma agenda (atualizando o status para 'Arquivada')
def arquivar_agenda(agenda_id):
    sheet = spreadsheet.get_worksheet(0)
    agenda_row = sheet.find(str(agenda_id))
    if agenda_row:
        sheet.update_cell(agenda_row.row, 5, 'Arquivada')  # Atualiza o status para "Arquivada"

# Função para restaurar uma agenda (atualizando o status para 'Ativa')
def restaurar_agenda(agenda_id):
    sheet = spreadsheet.get_worksheet(0)
    agenda_row = sheet.find(str(agenda_id))
    if agenda_row:
        sheet.update_cell(agenda_row.row, 5, 'Ativa')  # Atualiza o status para "Ativa"

# Função para duplicar uma agenda
def duplicar_agenda(agenda_id):
    sheet = spreadsheet.get_worksheet(0)
    agenda_row = sheet.find(str(agenda_id))
    if agenda_row:
        agenda_data = sheet.row_values(agenda_row.row)
        nova_agenda = agenda_data[:]
        nova_agenda[0] = nova_agenda[0] + " - Cópia"  # Ajuste o nome para indicar que é uma cópia
        sheet.append_row(nova_agenda)

# Rota principal para mostrar as agendas
@app.route('/')
def index():
    agendas = carregar_agendas()  # Carrega as agendas da planilha
    return render_template('index.html', agendas=agendas)

# Rota para criar uma nova agenda
@app.route('/criar-agenda', methods=['GET', 'POST'])
def criar_agenda_route():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        dias = request.form.getlist('dias')
        criar_agenda(nome, descricao, dias)  # Chama a função para gravar na planilha
        return redirect(url_for('index'))  # Redireciona de volta para a página principal
    return render_template('criar_agenda.html')

# Rota para editar uma agenda
@app.route('/editar-agenda/<int:agenda_id>', methods=['GET', 'POST'])
def editar_agenda_route(agenda_id):
    agenda = next((a for a in carregar_agendas() if a['id'] == agenda_id), None)
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        dias = request.form.getlist('dias')
        editar_agenda(agenda_id, nome, descricao, dias)  # Atualiza a agenda na planilha
        return redirect(url_for('ver_agenda', agenda_id=agenda_id))
    return render_template('editar_agenda.html', agenda=agenda)

# Rota para ver os detalhes de uma agenda
@app.route('/agenda/<int:agenda_id>')
def ver_agenda(agenda_id):
    agenda = next((a for a in carregar_agendas() if a['id'] == agenda_id), None)
    if not agenda:
        return redirect(url_for('index'))
    return render_template('agenda.html', agenda=agenda)

# Rota para excluir uma agenda
@app.route('/excluir-agenda/<int:agenda_id>')
def excluir_agenda_route(agenda_id):
    excluir_agenda(agenda_id)  # Exclui a agenda da planilha
    return redirect(url_for('index'))  # Redireciona de volta para a página principal

# Rota para arquivar uma agenda
@app.route('/arquivar-agenda/<int:agenda_id>')
def arquivar_agenda_route(agenda_id):
    arquivar_agenda(agenda_id)  # Arquiva a agenda na planilha
    return redirect(url_for('index'))  # Redireciona de volta para a página principal

# Rota para restaurar uma agenda
@app.route('/restaurar-agenda/<int:agenda_id>')
def restaurar_agenda_route(agenda_id):
    restaurar_agenda(agenda_id)  # Restaura a agenda na planilha
    return redirect(url_for('index'))  # Redireciona de volta para a página principal

# Rota para duplicar uma agenda
@app.route('/duplicar-agenda/<int:agenda_id>')
def duplicar_agenda_route(agenda_id):
    duplicar_agenda(agenda_id)  # Duplica a agenda na planilha
    return redirect(url_for('index'))  # Redireciona de volta para a página principal

if __name__ == '__main__':
    app.run(debug=True)
