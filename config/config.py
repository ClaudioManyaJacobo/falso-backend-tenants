import pymssql
from flask import flash

class Config:
    SQL_SERVER = '172.22.15.132'  
    SQL_USER = 'sa'     
    SQL_PASSWORD = 'GrupoHexagonal#0112'  
    SQL_DATABASE = 'multitenants' 
    SECRET_KEY = 'src_kay'  
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
    
    
def get_db_connection():
    try:
        connection = pymssql.connect(
            server=Config.SQL_SERVER,
            user=Config.SQL_USER,
            password=Config.SQL_PASSWORD,
            database=Config.SQL_DATABASE
        )
        return connection
    except pymssql.Error as e:
        flash(f'Error de conexión a la base de datos: {e}', 'error')
        return None