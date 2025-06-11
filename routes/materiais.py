from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from src.models import db, Material
from datetime import datetime

materiais_bp = Blueprint('materiais', __name__)

@materiais_bp.route('/')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Material.query
    
    if search:
        query = query.filter(
            Material.nome.contains(search) | 
            Material.codigo.contains(search) |
            Material.descricao.contains(search)
        )
    
    materiais = query.order_by(Material.nome).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('materiais/listar.html', materiais=materiais, search=search)

@materiais_bp.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        codigo = request.form.get('codigo')
        preco_unitario = request.form.get('preco_unitario')
        quantidade_estoque = request.form.get('quantidade_estoque', 0)
        unidade_medida = request.form.get('unidade_medida', 'UN')
        
        if not all([nome, codigo, preco_unitario]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('materiais/cadastrar.html')
        
        if Material.query.filter_by(codigo=codigo).first():
            flash('Este código já está cadastrado.', 'error')
            return render_template('materiais/cadastrar.html')
        
        try:
            material = Material(
                nome=nome,
                descricao=descricao,
                codigo=codigo,
                preco_unitario=float(preco_unitario),
                quantidade_estoque=int(quantidade_estoque),
                unidade_medida=unidade_medida
            )
            db.session.add(material)
            db.session.commit()
            flash('Material cadastrado com sucesso!', 'success')
            return redirect(url_for('materiais.listar'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar material.', 'error')
    
    return render_template('materiais/cadastrar.html')

@materiais_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    material = Material.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        codigo = request.form.get('codigo')
        preco_unitario = request.form.get('preco_unitario')
        quantidade_estoque = request.form.get('quantidade_estoque')
        unidade_medida = request.form.get('unidade_medida')
        
        if not all([nome, codigo, preco_unitario]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('materiais/editar.html', material=material)
        
        # Verificar se o código já existe em outro material
        existing = Material.query.filter_by(codigo=codigo).first()
        if existing and existing.id != material.id:
            flash('Este código já está cadastrado.', 'error')
            return render_template('materiais/editar.html', material=material)
        
        try:
            material.nome = nome
            material.descricao = descricao
            material.codigo = codigo
            material.preco_unitario = float(preco_unitario)
            material.quantidade_estoque = int(quantidade_estoque)
            material.unidade_medida = unidade_medida
            
            db.session.commit()
            flash('Material atualizado com sucesso!', 'success')
            return redirect(url_for('materiais.listar'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar material.', 'error')
    
    return render_template('materiais/editar.html', material=material)

@materiais_bp.route('/visualizar/<int:id>')
@login_required
def visualizar(id):
    material = Material.query.get_or_404(id)
    return render_template('materiais/visualizar.html', material=material)

@materiais_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    material = Material.query.get_or_404(id)
    
    # Verificar se o material está sendo usado em orçamentos
    if material.itens_orcamento:
        flash('Não é possível excluir este material pois ele está sendo usado em orçamentos.', 'error')
        return redirect(url_for('materiais.listar'))
    
    try:
        db.session.delete(material)
        db.session.commit()
        flash('Material excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir material.', 'error')
    
    return redirect(url_for('materiais.listar'))

@materiais_bp.route('/api/buscar')
@login_required
def api_buscar():
    """API para buscar materiais (usado em orçamentos)"""
    search = request.args.get('q', '')
    
    if len(search) < 2:
        return jsonify([])
    
    materiais = Material.query.filter(
        Material.nome.contains(search) | 
        Material.codigo.contains(search)
    ).limit(10).all()
    
    result = []
    for material in materiais:
        result.append({
            'id': material.id,
            'nome': material.nome,
            'codigo': material.codigo,
            'preco_unitario': float(material.preco_unitario),
            'unidade_medida': material.unidade_medida,
            'estoque': material.quantidade_estoque
        })
    
    return jsonify(result)

@materiais_bp.route('/ajustar-estoque/<int:id>', methods=['POST'])
@login_required
def ajustar_estoque(id):
    material = Material.query.get_or_404(id)
    
    try:
        nova_quantidade = int(request.form.get('nova_quantidade'))
        material.quantidade_estoque = nova_quantidade
        db.session.commit()
        flash('Estoque ajustado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao ajustar estoque.', 'error')
    
    return redirect(url_for('materiais.visualizar', id=id))


@materiais_bp.route('/api/buscar')
@login_required
