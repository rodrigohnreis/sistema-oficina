from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from src.models import db, Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('auth/login.html')
        
        user = Usuario.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.ativo:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Email ou senha inválidos.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/cadastrar-usuario', methods=['GET', 'POST'])
@login_required
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([nome, email, password, confirm_password]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('auth/cadastrar_usuario.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('auth/cadastrar_usuario.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return render_template('auth/cadastrar_usuario.html')
        
        try:
            novo_usuario = Usuario(nome=nome, email=email)
            novo_usuario.set_password(password)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('auth.listar_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar usuário.', 'error')
    
    return render_template('auth/cadastrar_usuario.html')

@auth_bp.route('/usuarios')
@login_required
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('auth/listar_usuarios.html', usuarios=usuarios)

@auth_bp.route('/usuario/<int:id>/toggle-status')
@login_required
def toggle_usuario_status(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.ativo = not usuario.ativo
    db.session.commit()
    
    status = "ativado" if usuario.ativo else "desativado"
    flash(f'Usuário {status} com sucesso!', 'success')
    return redirect(url_for('auth.listar_usuarios'))

