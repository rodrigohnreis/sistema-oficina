import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, redirect, url_for
from flask_login import LoginManager
from flask_cors import CORS
#from src.config import Config
#from src.models import db, Usuario
from config import Config
from models import db, Usuario

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config.from_object(Config)
    
    # Inicializar extensões
    db.init_app(app)
    CORS(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Registrar blueprints
  #  from src.routes.auth import auth_bp
   # from src.routes.dashboard import dashboard_bp
   # from src.routes.clientes import clientes_bp
   # from src.routes.materiais import materiais_bp
   # from src.routes.orcamentos import orcamentos_bp
   # from src.routes.ordens import ordens_bp
   # from src.routes.notas_fiscais import notas_fiscais_bp
   # from src.routes.relatorios import relatorios_bp

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.clientes import clientes_bp
    from routes.materiais import materiais_bp
    from routes.orcamentos import orcamentos_bp
    from routes.ordens import ordens_bp
    from routes.notas_fiscais import notas_fiscais_bp
    from routes.relatorios import relatorios_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(materiais_bp, url_prefix='/materiais')
    app.register_blueprint(orcamentos_bp, url_prefix='/orcamentos')
    app.register_blueprint(ordens_bp, url_prefix='/ordens')
    app.register_blueprint(notas_fiscais_bp, url_prefix='/notas-fiscais')
    app.register_blueprint(relatorios_bp, url_prefix='/relatorios')
    
    # Adicionar filtros personalizados para templates
    @app.template_filter('format_cpf_cnpj')
    def format_cpf_cnpj_filter(cpf_cnpj):
        if not cpf_cnpj:
            return ''
        
        cpf_cnpj = ''.join(filter(str.isdigit, cpf_cnpj))
        
        if len(cpf_cnpj) == 11:  # CPF
            return f'{cpf_cnpj[:3]}.{cpf_cnpj[3:6]}.{cpf_cnpj[6:9]}-{cpf_cnpj[9:]}'
        elif len(cpf_cnpj) == 14:  # CNPJ
            return f'{cpf_cnpj[:2]}.{cpf_cnpj[2:5]}.{cpf_cnpj[5:8]}/{cpf_cnpj[8:12]}-{cpf_cnpj[12:]}'
        else:
            return cpf_cnpj
    
    # Criar tabelas e usuário master
    with app.app_context():
        db.create_all()
        
        # Criar usuário master se não existir
        if not Usuario.query.filter_by(email='rodrigo@lantercar.com').first():
            usuario_master = Usuario(
                nome='Rodrigo',
                email='rodrigo@lantercar.com'
            )
            usuario_master.set_password('1234')
            db.session.add(usuario_master)
            db.session.commit()
            print("Usuário master criado: rodrigo@lantercar.com / 1234")
    
    return app

app = create_app()

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return redirect(url_for('auth.login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host='0.0.0.0', port=port, debug=debug)

