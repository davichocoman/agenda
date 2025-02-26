from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dados fictícios para desenvolvimento
agendas = [
    {
        'id': 1,
        'nome': 'Agenda 1',
        'descricao': 'Descrição da Agenda 1',
        'dias': ['segunda-feira', 'terca-feira']
    },
    {
        'id': 2,
        'nome': 'Agenda 2',
        'descricao': 'Descrição da Agenda 2',
        'dias': ['quarta-feira', 'quinta-feira']
    }
]

@app.route('/')
def index():
    return render_template('index.html', agendas=agendas)

@app.route('/criar-agenda', methods=['GET', 'POST'])
def criar_agenda():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']  # Verifique se esse campo está presente no formulário HTML
        dias = request.form.getlist('dias')
        nova_agenda = {'id': len(agendas) + 1, 'nome': nome, 'descricao': descricao, 'dias': dias, 'tarefas': {}}
        agendas.append(nova_agenda)
        return redirect(url_for('ver_agenda', agenda_id=nova_agenda['id']))
    return render_template('criar_agenda.html')

@app.route('/editar-agenda/<int:agenda_id>', methods=['GET', 'POST'])
def editar_agenda(agenda_id):
    agenda = next((a for a in agendas if a['id'] == agenda_id), None)
    if request.method == 'POST':
        agenda['nome'] = request.form['nome']
        agenda['descricao'] = request.form['descricao']
        agenda['dias'] = request.form.getlist('dias')
        return redirect(url_for('ver_agenda', agenda_id=agenda.id))
    return render_template('editar_agenda.html', agenda=agenda)

@app.route('/excluir-agenda/<int:agenda_id>')
def excluir_agenda(agenda_id):
    global agendas
    agendas = [agenda for agenda in agendas if agenda['id'] != agenda_id]
    return redirect(url_for('index'))

@app.route('/agenda/<int:agenda_id>')
def ver_agenda(agenda_id):
    agenda = next((a for a in agendas if a['id'] == agenda_id), None)
    if not agenda:
        return redirect(url_for('index'))
    return render_template('agenda.html', agenda=agenda)

@app.route('/agenda/<int:agenda_id>/dia/<dia>', methods=['GET', 'POST'])
def ver_dia(agenda_id, dia):
    agenda = next((a for a in agendas if a['id'] == agenda_id), None)
    if not agenda:
        return redirect(url_for('index'))

    if request.method == 'POST':
        tarefa = request.form['tarefa']
        horario = request.form['horario']
        descricao = request.form['descricao']
        link = request.form.get('link', '')
        progresso = request.form['progresso']

        if dia not in agenda['tarefas']:
            agenda['tarefas'][dia] = []

        agenda['tarefas'][dia].append({
            'horario': horario,
            'descricao': descricao,
            'tarefa': tarefa,
            'link': link,
            'progresso': progresso
        })

        # Ordena tarefas pelo horário
        agenda['tarefas'][dia].sort(key=lambda t: t['horario'])

        return redirect(url_for('ver_dia', agenda_id=agenda_id, dia=dia))

    return render_template('dia.html', agenda=agenda, dia=dia)


@app.route('/agenda/<int:agenda_id>/dia/<dia>/editar_tarefa/<int:tarefa_id>', methods=['GET', 'POST'])
def editar_tarefa(agenda_id, dia, tarefa_id):
    agenda = next((a for a in agendas if a['id'] == agenda_id), None)
    if not agenda:
        return redirect(url_for('index'))

    tarefa = agenda['tarefas'][dia][tarefa_id]

    if request.method == 'POST':
        tarefa['tarefa'] = request.form['tarefa']
        tarefa['horario'] = request.form['horario']
        tarefa['descricao'] = request.form['descricao']
        tarefa['link'] = request.form.get('link', '')
        tarefa['progresso'] = request.form['progresso']  # Atualiza progresso

        # Ordena tarefas pelo horário
        agenda['tarefas'][dia].sort(key=lambda t: t['horario'])

        return redirect(url_for('ver_dia', agenda_id=agenda_id, dia=dia))

    return render_template('editar_tarefa.html', agenda=agenda, dia=dia, tarefa=tarefa, tarefa_id=tarefa_id)

if __name__ == '__main__':
    app.run(debug=True)

