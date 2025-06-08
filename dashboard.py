from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.models import Cliente, Material, Orcamento, OrdemServico

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Estatísticas para o dashboard
    total_clientes = Cliente.query.count()
    total_materiais = Material.query.count()
    orcamentos_pendentes = Orcamento.query.filter_by(status='pendente').count()
    ordens_em_andamento = OrdemServico.query.filter_by(status='em_andamento').count()
    
    # Últimos orçamentos
    ultimos_orcamentos = Orcamento.query.order_by(Orcamento.data_orcamento.desc()).limit(5).all()
    
    return render_template('dashboard/index.html',
                         total_clientes=total_clientes,
                         total_materiais=total_materiais,
                         orcamentos_pendentes=orcamentos_pendentes,
                         ordens_em_andamento=ordens_em_andamento,
                         ultimos_orcamentos=ultimos_orcamentos)

