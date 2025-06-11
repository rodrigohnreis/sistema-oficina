from flask import Blueprint, render_template, redirect, url_for, flash
from models import Usuario
from extensions import db
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/cadastrar-usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['password']
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado!', 'danger')
            return redirect(url_for('auth.cadastrar_usuario'))
        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            password_hash=generate_password_hash(senha)
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('auth.listar_usuarios'))
    
    return render_template('auth/cadastrar_usuario.html')