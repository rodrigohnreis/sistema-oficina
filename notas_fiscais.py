from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from src.models import db, NotaFiscal, OrdemServico
from datetime import datetime

notas_fiscais_bp = Blueprint('notas_fiscais', __name__)

@notas_fiscais_bp.route('/')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    
    query = NotaFiscal.query.join(OrdemServico).join(OrdemServico.orcamento).join(OrdemServico.orcamento.cliente)
    
    if search:
        query = query.filter(
            NotaFiscal.numero_nf.contains(search) |
            OrdemServico.numero_ordem.contains(search) |
            OrdemServico.orcamento.cliente.nome.contains(search)
        )
    
    if status_filter:
        query = query.filter(NotaFiscal.status == status_filter)
    
    notas_fiscais = query.order_by(NotaFiscal.data_emissao.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('notas_fiscais/listar.html', 
                         notas_fiscais=notas_fiscais, 
                         search=search, 
                         status_filter=status_filter)

@notas_fiscais_bp.route('/visualizar/<int:id>')
@login_required
def visualizar(id):
    nota_fiscal = NotaFiscal.query.get_or_404(id)
    return render_template('notas_fiscais/visualizar.html', nota_fiscal=nota_fiscal)

@notas_fiscais_bp.route('/pdf/<int:id>')
@login_required
def gerar_pdf(id):
    nota_fiscal = NotaFiscal.query.get_or_404(id)
    
    try:
        from src.utils.pdf_generator import gerar_pdf_nota_fiscal
        pdf_content = gerar_pdf_nota_fiscal(nota_fiscal)
        
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=nota_fiscal_{nota_fiscal.numero_nf}.pdf'
        
        return response
    except Exception as e:
        flash('Erro ao gerar PDF da nota fiscal.', 'error')
        return redirect(url_for('notas_fiscais.visualizar', id=id))

@notas_fiscais_bp.route('/cancelar/<int:id>')
@login_required
def cancelar(id):
    nota_fiscal = NotaFiscal.query.get_or_404(id)
    
    if nota_fiscal.status != 'emitida':
        flash('Esta nota fiscal não pode ser cancelada.', 'error')
        return redirect(url_for('notas_fiscais.visualizar', id=id))
    
    try:
        nota_fiscal.status = 'cancelada'
        db.session.commit()
        flash('Nota fiscal cancelada com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao cancelar nota fiscal.', 'error')
    
    return redirect(url_for('notas_fiscais.visualizar', id=id))

