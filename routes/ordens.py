from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from src.models import db, OrdemServico, Contrato, NotaFiscal, Orcamento
from datetime import datetime
import uuid

ordens_bp = Blueprint('ordens', __name__)

def gerar_numero_ordem():
    """Gerar número único para ordem de serviço"""
    ano = datetime.now().year
    ultima_ordem = OrdemServico.query.filter(
        OrdemServico.numero_ordem.like(f'OS{ano}%')
    ).order_by(OrdemServico.id.desc()).first()
    
    if ultima_ordem:
        ultimo_numero = int(ultima_ordem.numero_ordem[-4:])
        novo_numero = ultimo_numero + 1
    else:
        novo_numero = 1
    
    return f'OS{ano}{novo_numero:04d}'

def gerar_numero_contrato():
    """Gerar número único para contrato"""
    ano = datetime.now().year
    ultimo_contrato = Contrato.query.filter(
        Contrato.numero_contrato.like(f'CT{ano}%')
    ).order_by(Contrato.id.desc()).first()
    
    if ultimo_contrato:
        ultimo_numero = int(ultimo_contrato.numero_contrato[-4:])
        novo_numero = ultimo_numero + 1
    else:
        novo_numero = 1
    
    return f'CT{ano}{novo_numero:04d}'

def criar_ordem_automatica(orcamento_id):
    """Criar ordem de serviço e contrato automaticamente após aceite do orçamento"""
    try:
        orcamento = Orcamento.query.get(orcamento_id)
        if not orcamento or orcamento.status != 'aceito':
            return False
        
        # Criar ordem de serviço
        ordem = OrdemServico(
            orcamento_id=orcamento.id,
            numero_ordem=gerar_numero_ordem(),
            observacoes=f'Ordem criada automaticamente a partir do orçamento {orcamento.numero_orcamento}'
        )
        db.session.add(ordem)
        db.session.flush()  # Para obter o ID
        
        # Criar contrato
        termos_padrao = """
TERMOS E CONDIÇÕES DO CONTRATO DE PRESTAÇÃO DE SERVIÇOS

1. OBJETO: O presente contrato tem por objeto a prestação de serviços de oficina mecânica conforme especificado no orçamento aprovado.

2. PRAZO: Os serviços serão executados no prazo acordado entre as partes.

3. PREÇO E FORMA DE PAGAMENTO: O valor total dos serviços é o constante no orçamento aprovado, sendo o pagamento efetuado conforme acordado.

4. GARANTIA: Os serviços prestados possuem garantia conforme legislação vigente e políticas da empresa.

5. RESPONSABILIDADES: A LANTERCAR se responsabiliza pela execução dos serviços com qualidade e dentro do prazo acordado.

6. FORO: Fica eleito o foro da comarca onde se encontra a sede da LANTERCAR para dirimir quaisquer questões oriundas do presente contrato.
        """
        
        contrato = Contrato(
            ordem_servico_id=ordem.id,
            numero_contrato=gerar_numero_contrato(),
            termos_condicoes=termos_padrao
        )
        db.session.add(contrato)
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        return False

@ordens_bp.route('/')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    
    query = OrdemServico.query.join(Orcamento).join(Orcamento.cliente)
    
    if search:
        query = query.filter(
            OrdemServico.numero_ordem.contains(search) |
            Orcamento.numero_orcamento.contains(search) |
            Orcamento.cliente.nome.contains(search)
        )
    
    if status_filter:
        query = query.filter(OrdemServico.status == status_filter)
    
    ordens = query.order_by(OrdemServico.data_inicio.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('ordens/listar.html', 
                         ordens=ordens, 
                         search=search, 
                         status_filter=status_filter)

@ordens_bp.route('/visualizar/<int:id>')
@login_required
def visualizar(id):
    ordem = OrdemServico.query.get_or_404(id)
    return render_template('ordens/visualizar.html', ordem=ordem)

@ordens_bp.route('/iniciar/<int:id>')
@login_required
def iniciar(id):
    ordem = OrdemServico.query.get_or_404(id)
    
    if ordem.status != 'em_andamento':
        flash('Esta ordem de serviço não pode ser iniciada.', 'error')
        return redirect(url_for('ordens.visualizar', id=id))
    
    try:
        ordem.data_inicio = datetime.now()
        db.session.commit()
        flash('Ordem de serviço iniciada!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao iniciar ordem de serviço.', 'error')
    
    return redirect(url_for('ordens.visualizar', id=id))

@ordens_bp.route('/concluir/<int:id>', methods=['GET', 'POST'])
@login_required
def concluir(id):
    ordem = OrdemServico.query.get_or_404(id)
    
    if ordem.status != 'em_andamento':
        flash('Esta ordem de serviço não pode ser concluída.', 'error')
        return redirect(url_for('ordens.visualizar', id=id))
    
    if request.method == 'POST':
        observacoes_conclusao = request.form.get('observacoes_conclusao', '')
        
        try:
            ordem.status = 'concluido'
            ordem.data_conclusao = datetime.now()
            if observacoes_conclusao:
                ordem.observacoes = (ordem.observacoes or '') + f'\n\nConclusão: {observacoes_conclusao}'
            
            db.session.commit()
            
            # Gerar nota fiscal automaticamente
            gerar_nota_fiscal_automatica(ordem.id)
            
            flash('Ordem de serviço concluída! Nota fiscal gerada automaticamente.', 'success')
            return redirect(url_for('ordens.visualizar', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao concluir ordem de serviço.', 'error')
    
    return render_template('ordens/concluir.html', ordem=ordem)

@ordens_bp.route('/cancelar/<int:id>', methods=['GET', 'POST'])
@login_required
def cancelar(id):
    ordem = OrdemServico.query.get_or_404(id)
    
    if ordem.status == 'concluido':
        flash('Não é possível cancelar uma ordem de serviço concluída.', 'error')
        return redirect(url_for('ordens.visualizar', id=id))
    
    if request.method == 'POST':
        motivo_cancelamento = request.form.get('motivo_cancelamento', '')
        
        try:
            ordem.status = 'cancelado'
            if motivo_cancelamento:
                ordem.observacoes = (ordem.observacoes or '') + f'\n\nCancelamento: {motivo_cancelamento}'
            
            # Cancelar contrato relacionado
            if ordem.contrato:
                ordem.contrato.status = 'cancelado'
            
            db.session.commit()
            flash('Ordem de serviço cancelada.', 'success')
            return redirect(url_for('ordens.visualizar', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cancelar ordem de serviço.', 'error')
    
    return render_template('ordens/cancelar.html', ordem=ordem)

@ordens_bp.route('/contrato/pdf/<int:id>')
@login_required
def gerar_pdf_contrato(id):
    ordem = OrdemServico.query.get_or_404(id)
    
    if not ordem.contrato:
        flash('Esta ordem de serviço não possui contrato.', 'error')
        return redirect(url_for('ordens.visualizar', id=id))
    
    try:
        from src.utils.pdf_generator import gerar_pdf_contrato
        pdf_content = gerar_pdf_contrato(ordem.contrato)
        
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=contrato_{ordem.contrato.numero_contrato}.pdf'
        
        return response
    except Exception as e:
        flash('Erro ao gerar PDF do contrato.', 'error')
        return redirect(url_for('ordens.visualizar', id=id))

@ordens_bp.route('/ordem/pdf/<int:id>')
@login_required
def gerar_pdf_ordem(id):
    ordem = OrdemServico.query.get_or_404(id)
    
    try:
        from src.utils.pdf_generator import gerar_pdf_ordem_servico
        pdf_content = gerar_pdf_ordem_servico(ordem)
        
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=ordem_servico_{ordem.numero_ordem}.pdf'
        
        return response
    except Exception as e:
        flash('Erro ao gerar PDF da ordem de serviço.', 'error')
        return redirect(url_for('ordens.visualizar', id=id))

def gerar_nota_fiscal_automatica(ordem_id):
    """Gerar nota fiscal automaticamente quando ordem é concluída"""
    try:
        ordem = OrdemServico.query.get(ordem_id)
        if not ordem or ordem.status != 'concluido':
            return False
        
        # Verificar se já existe nota fiscal
        if ordem.nota_fiscal:
            return True
        
        # Gerar número da nota fiscal
        ano = datetime.now().year
        ultima_nf = NotaFiscal.query.filter(
            NotaFiscal.numero_nf.like(f'NF{ano}%')
        ).order_by(NotaFiscal.id.desc()).first()
        
        if ultima_nf:
            ultimo_numero = int(ultima_nf.numero_nf[-4:])
            novo_numero = ultimo_numero + 1
        else:
            novo_numero = 1
        
        numero_nf = f'NF{ano}{novo_numero:04d}'
        
        # Criar nota fiscal
        nota_fiscal = NotaFiscal(
            ordem_servico_id=ordem.id,
            numero_nf=numero_nf,
            valor_total=ordem.orcamento.valor_total
        )
        
        db.session.add(nota_fiscal)
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        return False

