from flask import render_template, request, redirect, url_for, flash, session
from controllers.event_controller import EventController
from controllers.user_controller import UserController
from functools import wraps
from app import app  

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para continuar.', 'error')
            tenant_name = kwargs.get('tenant_name')
            return redirect(url_for('login', tenant_name=tenant_name))
        return f(*args, **kwargs)
    return decorated_function

user_controller = UserController()
event_controller = EventController()


@app.route('/<tenant_name>/login', methods=['GET', 'POST'])
def login(tenant_name):
    return user_controller.login(tenant_name)

@app.route('/<tenant_name>/register', methods=['GET', 'POST'])
def register(tenant_name):
    return user_controller.register(tenant_name)

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('login', tenant_name='default'))

@app.route('/<tenant_name>/events', methods=['GET'])
@login_required
def list_events(tenant_name):
    return event_controller.list_events(tenant_name)

@app.route('/<tenant_name>/events/new', methods=['GET', 'POST'])
@login_required
def new_event(tenant_name):
    return event_controller.new_event(tenant_name)

@app.route('/<tenant_name>/events/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(tenant_name, id):
    return event_controller.edit_event(tenant_name, id)

@app.route('/<tenant_name>/events/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_event(tenant_name, id):
    return event_controller.delete_event(tenant_name, id)
