class Event:
    def __init__(self, id, name, description, date, location, tenant_id):
        self.id = id
        self.name = name
        self.description = description
        self.date = date
        self.location = location
        self.tenant_id = tenant_id
        """
        self.image_url = image_url
        self.modalidad = modalidad
        self.incio = inicio
        self.fin = fin
        self.valoracion = valoracion
        
        ##########################
        
        # Relaciones 
        self.ponente = ponente
        self.correo_ponente = correo_ponente 
        """