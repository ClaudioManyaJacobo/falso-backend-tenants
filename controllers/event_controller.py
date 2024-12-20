import pymssql
from flask import flash, redirect, render_template, url_for, request
from datetime import datetime
from models.Event.event import Event
from config.config import get_db_connection

class EventController:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if not self.connection:
            self.connection = get_db_connection()
        return self.connection

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def tenant_exists(self, tenant_name):
        connection = self.get_connection()
        if not connection:
            return False

        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM tenants WHERE name = %s", (tenant_name,))
            tenant = cursor.fetchone()
            return bool(tenant)
        finally:
            cursor.close()

    def list_events(self, tenant_name):
        if not self.tenant_exists(tenant_name):
            return render_template('error/error.html', message='Tenant no encontrado')

        connection = self.get_connection()
        if not connection:
            return render_template('error/error.html', message='Error al conectar con la base de datos')

        cursor = connection.cursor()
        try:
            query = "SELECT * FROM events WHERE tenant_name = %s"
            cursor.execute(query, (tenant_name,))
            events = cursor.fetchall()

            events = [
                Event(id=row[0], name=row[1], description=row[2], date=row[3], location=row[4], tenant_id=row[5])
                for row in events
            ]
            css_file = f"{tenant_name.lower()}/index.css"
            return render_template('events.html', events=events, tenant_name=tenant_name, css_file=css_file)
        finally:
            cursor.close()

    def new_event(self, tenant_name):
        if not self.tenant_exists(tenant_name):
            flash('Tenant no encontrado.', 'error')
            return redirect(url_for('list_events', tenant_name=tenant_name))

        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            date_str = request.form['date']
            location = request.form['location']

            if not name or not description or not date_str or not location:
                flash('Todos los campos son obligatorios.', 'error')
                return render_template('new_event.html', tenant_name=tenant_name)

            try:
                date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('La fecha ingresada no tiene un formato válido. Use YYYY-MM-DDTHH:MM.', 'error')
                return render_template('new_event.html', tenant_name=tenant_name)

            connection = self.get_connection()
            if not connection:
                return render_template('new_event.html', tenant_name=tenant_name)

            cursor = connection.cursor()
            try:
                query = """
                INSERT INTO events (name, description, date, location, tenant_name)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (name, description, date, location, tenant_name))
                connection.commit()
                flash('Evento creado exitosamente.', 'success')
                return redirect(url_for('list_events', tenant_name=tenant_name))
            finally:
                cursor.close()

        return render_template('new_event.html', tenant_name=tenant_name)

    def edit_event(self, tenant_name, id):
        if not self.tenant_exists(tenant_name):
            flash('Tenant no encontrado.', 'error')
            return redirect(url_for('list_events', tenant_name=tenant_name))

        connection = self.get_connection()
        if not connection:
            return redirect(url_for('list_events', tenant_name=tenant_name))

        cursor = connection.cursor(as_dict=True) 
        try:
            # Recuperar el evento por ID y tenant
            query = "SELECT * FROM events WHERE id = %s AND tenant_name = %s"
            cursor.execute(query, (id, tenant_name))
            event = cursor.fetchone()

            if not event:
                flash('Evento no encontrado.', 'error')
                return redirect(url_for('list_events', tenant_name=tenant_name))

            if request.method == 'POST':
                name = request.form['name']
                description = request.form['description']
                date_str = request.form['date']
                location = request.form['location']

                if not name or not description or not date_str or not location:
                    flash('Todos los campos son obligatorios.', 'error')
                    return render_template('edit_event.html', event=event, tenant_name=tenant_name)

                try:
                    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('La fecha ingresada no tiene un formato válido. Use YYYY-MM-DDTHH:MM.', 'error')
                    return render_template('edit_event.html', event=event, tenant_name=tenant_name)

                # Actualizar el evento en la base de datos
                query = """
                UPDATE events
                SET name = %s, description = %s, date = %s, location = %s
                WHERE id = %s AND tenant_name = %s
                """
                cursor.execute(query, (name, description, date, location, id, tenant_name))
                connection.commit()
                flash('Evento actualizado exitosamente.', 'success')
                return redirect(url_for('list_events', tenant_name=tenant_name))

            # Renderizar la página de edición con el evento recuperado
            return render_template('edit_event.html', event=event, tenant_name=tenant_name)
        finally:
            cursor.close()


    def delete_event(self, tenant_name, id):
        if not self.tenant_exists(tenant_name):
            flash('Tenant no encontrado.', 'error')
            return redirect(url_for('list_events', tenant_name=tenant_name))

        connection = self.get_connection()
        if not connection:
            return redirect(url_for('list_events', tenant_name=tenant_name))

        cursor = connection.cursor()
        try:
            query = "SELECT * FROM events WHERE id = %s AND tenant_name = %s"
            cursor.execute(query, (id, tenant_name))
            event = cursor.fetchone()

            if not event:
                flash('Evento no encontrado.', 'error')
                return redirect(url_for('list_events', tenant_name=tenant_name))

            if request.method == 'POST':
                query = "DELETE FROM events WHERE id = %s AND tenant_name = %s"
                cursor.execute(query, (id, tenant_name))
                connection.commit()
                flash('Evento eliminado exitosamente.', 'success')
                return redirect(url_for('list_events', tenant_name=tenant_name))

            return render_template('delete_event.html', event=event, tenant_name=tenant_name)
        finally:
            cursor.close()

    def __del__(self):
        self.close_connection()
