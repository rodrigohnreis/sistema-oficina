from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from src.models import db, Cliente
from datetime import datetime

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Cliente.query
    
    if search:
        query = query.filter(
            Cliente.nome.contains(search) | 
            Cliente.cpf_cnpj.contains(search) |
            Cliente.email.contains(search) |
            Cliente.telefone.contains(search)
        )
    
    clientes = query.order_by(Cliente.nome).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('clientes/listar.html', clientes=clientes, search=search)

@clientes_bp.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf_cnpj = request.form.get('cpf_cnpj')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        endereco = request.form.get('endereco')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        cep = request.form.get('cep')
        
        if not all([nome, cpf_cnpj]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('clientes/cadastrar.html')
        
        # Remover caracteres especiais do CPF/CNPJ
        cpf_cnpj_clean = ''.join(filter(str.isdigit, cpf_cnpj))
        
        if Cliente.query.filter_by(cpf_cnpj=cpf_cnpj_clean).first():
            flash('Este CPF/CNPJ já está cadastrado.', 'error')
            return render_template('clientes/cadastrar.html')
        
        try:
            cliente = Cliente(
                nome=nome,
                cpf_cnpj=cpf_cnpj_clean,
                telefone=telefone,
                email=email,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                cep=cep
            )
            db.session.add(cliente)
            db.session.commit()
            flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('clientes.listar'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar cliente.', 'error')
    
    return render_template('clientes/cadastrar.html')

@clientes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf_cnpj = request.form.get('cpf_cnpj')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        endereco = request.form.get('endereco')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        cep = request.form.get('cep')
        
        if not all([nome, cpf_cnpj]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('clientes/editar.html', cliente=cliente)
        
        # Remover caracteres especiais do CPF/CNPJ
        cpf_cnpj_clean = ''.join(filter(str.isdigit, cpf_cnpj))
        
        # Verificar se o CPF/CNPJ já existe em outro cliente
        existing = Cliente.query.filter_by(cpf_cnpj=cpf_cnpj_clean).first()
        if existing and existing.id != cliente.id:
            flash('Este CPF/CNPJ já está cadastrado.', 'error')
            return render_template('clientes/editar.html', cliente=cliente)
        
        try:
            cliente.nome = nome
            cliente.cpf_cnpj = cpf_cnpj_clean
            cliente.telefone = telefone
            cliente.email = email
            cliente.endereco = endereco
            cliente.cidade = cidade
            cliente.estado = estado
            cliente.cep = cep
            
            db.session.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('clientes.listar'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar cliente.', 'error')
    
    return render_template('clientes/editar.html', cliente=cliente)

@clientes_bp.route('/visualizar/<int:id>')
@login_required
def visualizar(id):
    cliente = Cliente.query.get_or_404(id)
    
    # Buscar orçamentos do cliente
    orcamentos = cliente.orcamentos
    
    return render_template('clientes/visualizar.html', cliente=cliente, orcamentos=orcamentos)

@clientes_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    cliente = Cliente.query.get_or_404(id)
    
    # Verificar se o cliente possui orçamentos
    if cliente.orcamentos:
        flash('Não é possível excluir este cliente pois ele possui orçamentos cadastrados.', 'error')
        return redirect(url_for('clientes.listar'))
    
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir cliente.', 'error')
    
    return redirect(url_for('clientes.listar'))

@clientes_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar clientes (usado em orçamentos)"""
    search = request.args.get('q', '')
    
    if len(search) < 2:
        return jsonify([])
    
    clientes = Cliente.query.filter(
        Cliente.nome.contains(search) | 
        Cliente.cpf_cnpj.contains(search)
    ).limit(10).all()
    
    result = []
    for cliente in clientes:
        result.append({
            'id': cliente.id,
            'nome': cliente.nome,
            'cpf_cnpj': cliente.cpf_cnpj,
            'telefone': cliente.telefone,
            'email': cliente.email
        })
    
    return jsonify(result)

def format_cpf_cnpj(cpf_cnpj):
    """Formatar CPF/CNPJ para exibição"""
    if not cpf_cnpj:
        return ''
    
    cpf_cnpj = ''.join(filter(str.isdigit, cpf_cnpj))
    
    if len(cpf_cnpj) == 11:  # CPF
        return f'{cpf_cnpj[:3]}.{cpf_cnpj[3:6]}.{cpf_cnpj[6:9]}-{cpf_cnpj[9:]}'
    elif len(cpf_cnpj) == 14:  # CNPJ
        return f'{cpf_cnpj[:2]}.{cpf_cnpj[2:5]}.{cpf_cnpj[5:8]}/{cpf_cnpj[8:12]}-{cpf_cnpj[12:]}'
    else:
        return cpf_cnpj

# Registrar filtro para templates
@clientes_bp.app_template_filter('format_cpf_cnpj')
def format_cpf_cnpj_filter(cpf_cnpj):
    return format_cpf_cnpj(cpf_cnpj)


@clientes_bp.route('/api/buscar')
@login_required
def api_buscar():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    clientes = Cliente.query.filter(
        Cliente.nome.contains(query) |
        Cliente.cpf_cnpj.contains(query)
    ).limit(10).all()
    
    resultado = []
    for cliente in clientes:
        resultado.append({
            'id': cliente.id,
            'nome': cliente.nome,
            'cpf_cnpj': cliente.cpf_cnpj
        })
    
    return jsonify(resultado)

