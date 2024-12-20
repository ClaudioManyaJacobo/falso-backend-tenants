import bcrypt
from flask import render_template, request, flash, redirect, url_for, session
from models.User.user import User
from config.config import get_db_connection

class UserController:
    def __init__(self):
        self.connection = get_db_connection()

    def register(self, tenant_name):
        # Verificar que el tenant existe
        cursor = self.connection.cursor(as_dict=True)
        cursor.execute("SELECT id FROM tenants WHERE name = %s", (tenant_name,))
        tenant = cursor.fetchone()
        if not tenant:
            flash('Tenant no encontrado.', 'error')
            return redirect(url_for('home'))

        if request.method == 'POST':
            name = request.form['name']
            password = request.form['password']
            gmail = request.form['gmail']
            role = 'user'  # Por defecto, se registra como usuario

            if not name or not password or not gmail:
                flash('Todos los campos son obligatorios.', 'error')
                return render_template('register.html', tenant_name=tenant_name)

            # Hashea la contraseña
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insertar en la base de datos
            cursor.execute("""
                INSERT INTO users (name, password, gmail, role, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, hashed_password, gmail, role, tenant['id']))
            self.connection.commit()
            flash('Usuario registrado exitosamente.', 'success')
            return redirect(url_for('login', tenant_name=tenant_name))

        return render_template('register.html', tenant_name=tenant_name)
    
    
    def login(self, tenant_name):
        # Verificar que el tenant existe
        cursor = self.connection.cursor(as_dict=True)
        cursor.execute("SELECT id FROM tenants WHERE name = %s", (tenant_name,))
        tenant = cursor.fetchone()
        if not tenant:
            flash('Tenant no encontrado.', 'error')
            return redirect(url_for('home'))

        if request.method == 'POST':
            gmail = request.form['gmail']
            password = request.form['password']

            if not gmail or not password:
                flash('Todos los campos son obligatorios.', 'error')
                return render_template('login.html', tenant_name=tenant_name)

            # Buscar usuario por correo electrónico y tenant
            cursor.execute("""
                SELECT * FROM users WHERE gmail = %s AND tenant_id = %s
            """, (gmail, tenant['id']))
            user = cursor.fetchone()

            if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                flash('Credenciales inválidas.', 'error')
                return render_template('login.html', tenant_name=tenant_name)

            # Autenticar al usuario
            session['user_id'] = user['id']
            session['tenant_id'] = tenant['id']
            session['role'] = user['role']
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('list_events', tenant_name=tenant_name))

        return render_template('login.html', tenant_name=tenant_name)
