from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from src.models import db, Orcamento, OrcamentoItem, Cliente, Material
from datetime import datetime, timedelta
import uuid

orcamentos_bp = Blueprint('orcamentos', __name__)

def gerar_numero_orcamento():
    """Gerar número único para orçamento"""
    ano = datetime.now().year
    ultimo_orcamento = Orcamento.query.filter(
        Orcamento.numero_orcamento.like(f'ORC{ano}%')
    ).order_by(Orcamento.id.desc()).first()
    
    if ultimo_orcamento:
        ultimo_numero = int(ultimo_orcamento.numero_orcamento[-4:])
        novo_numero = ultimo_numero + 1
    else:
        novo_numero = 1
    
    return f'ORC{ano}{novo_numero:04d}'

@orcamentos_bp.route('/')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    
    query = Orcamento.query
    
    if search:
        query = query.join(Cliente).filter(
            Orcamento.numero_orcamento.contains(search) |
            Cliente.nome.contains(search) |
            Orcamento.descricao_servico.contains(search)
        )
    
    if status_filter:
        query = query.filter(Orcamento.status == status_filter)
    
    orcamentos = query.order_by(Orcamento.data_orcamento.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('orcamentos/listar.html', 
                         orcamentos=orcamentos, 
                         search=search, 
                         status_filter=status_filter)

@orcamentos_bp.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        descricao_servico = request.form.get('descricao_servico')
        valor_mao_obra = request.form.get('valor_mao_obra', 0)
        validade_dias = request.form.get('validade_dias', 30)
        observacoes = request.form.get('observacoes')
        
        if not all([cliente_id, descricao_servico]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('orcamentos/cadastrar.html')
        
        try:
            # Criar orçamento
            orcamento = Orcamento(
                cliente_id=int(cliente_id),
                usuario_id=current_user.id,
                numero_orcamento=gerar_numero_orcamento(),
                descricao_servico=descricao_servico,
                valor_mao_obra=float(valor_mao_obra),
                validade=datetime.now().date() + timedelta(days=int(validade_dias)),
                observacoes=observacoes
            )
            
            db.session.add(orcamento)
            db.session.flush()  # Para obter o ID
            
            # Adicionar itens do orçamento
            materiais_ids = request.form.getlist('material_id[]')
            quantidades = request.form.getlist('quantidade[]')
            precos = request.form.getlist('preco_unitario[]')
            
            for i, material_id in enumerate(materiais_ids):
                if material_id and quantidades[i] and precos[i]:
                    item = OrcamentoItem(
                        orcamento_id=orcamento.id,
                        material_id=int(material_id),
                        quantidade=float(quantidades[i]),
                        preco_unitario=float(precos[i])
                    )
                    item.calcular_subtotal()
                    db.session.add(item)
            
            # Calcular total
            orcamento.calcular_total()
            
            db.session.commit()
            flash('Orçamento cadastrado com sucesso!', 'success')
            return redirect(url_for('orcamentos.visualizar', id=orcamento.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar orçamento.', 'error')
    
    # Pré-selecionar cliente se fornecido na URL
    cliente_id = request.args.get('cliente_id')
    cliente_selecionado = None
    if cliente_id:
        cliente_selecionado = Cliente.query.get(cliente_id)
    
    return render_template('orcamentos/cadastrar.html', cliente_selecionado=cliente_selecionado)

@orcamentos_bp.route('/visualizar/<int:id>')
@login_required
def visualizar(id):
    orcamento = Orcamento.query.get_or_404(id)
    return render_template('orcamentos/visualizar.html', orcamento=orcamento)

@orcamentos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    orcamento = Orcamento.query.get_or_404(id)
    
    if orcamento.status != 'pendente':
        flash('Não é possível editar um orçamento que não está pendente.', 'error')
        return redirect(url_for('orcamentos.visualizar', id=id))
    
    if request.method == 'POST':
        try:
            orcamento.descricao_servico = request.form.get('descricao_servico')
            orcamento.valor_mao_obra = float(request.form.get('valor_mao_obra', 0))
            orcamento.observacoes = request.form.get('observacoes')
            
            validade_dias = int(request.form.get('validade_dias', 30))
            orcamento.validade = datetime.now().date() + timedelta(days=validade_dias)
            
            # Remover itens existentes
            for item in orcamento.itens:
                db.session.delete(item)
            
            # Adicionar novos itens
            materiais_ids = request.form.getlist('material_id[]')
            quantidades = request.form.getlist('quantidade[]')
            precos = request.form.getlist('preco_unitario[]')
            
            for i, material_id in enumerate(materiais_ids):
                if material_id and quantidades[i] and precos[i]:
                    item = OrcamentoItem(
                        orcamento_id=orcamento.id,
                        material_id=int(material_id),
                        quantidade=float(quantidades[i]),
                        preco_unitario=float(precos[i])
                    )
                    item.calcular_subtotal()
                    db.session.add(item)
            
            # Recalcular total
            orcamento.calcular_total()
            
            db.session.commit()
            flash('Orçamento atualizado com sucesso!', 'success')
            return redirect(url_for('orcamentos.visualizar', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar orçamento.', 'error')
    
    return render_template('orcamentos/editar.html', orcamento=orcamento)

@orcamentos_bp.route('/aceitar/<int:id>')
@login_required
def aceitar(id):
    orcamento = Orcamento.query.get_or_404(id)
    
    if orcamento.status != 'pendente':
        flash('Este orçamento não pode ser aceito.', 'error')
        return redirect(url_for('orcamentos.visualizar', id=id))
    
    try:
        orcamento.status = 'aceito'
        db.session.commit()
        
        # Criar ordem de serviço automaticamente
        from src.routes.ordens import criar_ordem_automatica
        criar_ordem_automatica(orcamento.id)
        
        flash('Orçamento aceito com sucesso! Ordem de serviço criada automaticamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao aceitar orçamento.', 'error')
    
    return redirect(url_for('orcamentos.visualizar', id=id))

@orcamentos_bp.route('/rejeitar/<int:id>')
@login_required
def rejeitar(id):
    orcamento = Orcamento.query.get_or_404(id)
    
    if orcamento.status != 'pendente':
        flash('Este orçamento não pode ser rejeitado.', 'error')
        return redirect(url_for('orcamentos.visualizar', id=id))
    
    try:
        orcamento.status = 'rejeitado'
        db.session.commit()
        flash('Orçamento rejeitado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao rejeitar orçamento.', 'error')
    
    return redirect(url_for('orcamentos.visualizar', id=id))

@orcamentos_bp.route('/pdf/<int:id>')
@login_required
def gerar_pdf(id):
    orcamento = Orcamento.query.get_or_404(id)
    
    try:
        from src.utils.pdf_generator import gerar_pdf_orcamento
        pdf_content = gerar_pdf_orcamento(orcamento)
        
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=orcamento_{orcamento.numero_orcamento}.pdf'
        
        return response
    except Exception as e:
        flash('Erro ao gerar PDF do orçamento.', 'error')
        return redirect(url_for('orcamentos.visualizar', id=id))

@orcamentos_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    orcamento = Orcamento.query.get_or_404(id)
    
    if orcamento.status == 'aceito':
        flash('Não é possível excluir um orçamento aceito.', 'error')
        return redirect(url_for('orcamentos.listar'))
    
    try:
        # Excluir itens primeiro
        for item in orcamento.itens:
            db.session.delete(item)
        
        db.session.delete(orcamento)
        db.session.commit()
        flash('Orçamento excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir orçamento.', 'error')
    
    return redirect(url_for('orcamentos.listar'))

