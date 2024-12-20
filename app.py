from flask import Flask
from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Importa las rutas después de configurar la aplicación
from routes.routes import *

if __name__ == '__main__':
    app.run(debug=True)
