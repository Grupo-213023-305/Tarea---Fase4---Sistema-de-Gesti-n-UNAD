# --- MÓDULO RESERVAS (Nicol Yeritza) ---
class Cliente(Entidad):
    patron_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    def __init__(self, nombre, email, telefono):
        super().__init__()
        self._historial = []
        self.nombre, self.email, self.telefono = nombre, email, telefono

    @property
    def nombre(self): return self._nombre
    @nombre.setter
    def nombre(self, v):
        if not v or len(v.strip()) < 3: raise ClienteError("Nombre muy corto.")
        self._nombre = v.strip().title()

    @property
    def email(self): return self._email
    @email.setter
    def email(self, v):
        if not re.match(self.patron_email, v): raise ClienteError("Email no válido.")
        self._email = v.lower()

    @property
    def telefono(self): return self._telefono
    @telefono.setter
    def telefono(self, v):
        if not re.fullmatch(r"\d{7,15}", str(v)): raise ClienteError("Teléfono debe ser numérico.")
        self._telefono = str(v)

    def agregar_reserva(self, reserva): self._historial.append(reserva)
    def describir(self): return f"Cliente: {self.nombre}"

class ServicioHeredado(Servicio):
    def __init__(self, nombre, tarifa):
        if tarifa <= 0: raise ServicioError("Tarifa debe ser positiva.")
        self.nombre, self.tarifa = nombre, tarifa
    def ajustar_costo(self, costo, desc, imp):
        return round(costo * (1 - desc) * (1 + imp), 2)

class ServicioSala(ServicioHeredado):
    def calcular_costo(self, horas, desc=0, imp=0.19):
        return self.ajustar_costo(self.tarifa * horas, desc, imp)

class ServicioAsesoria(ServicioHeredado):
    def calcular_costo(self, horas, desc=0, imp=0.19):
        return self.ajustar_costo(self.tarifa * horas * 1.2, desc, imp)

class Reserva(Entidad):
    def __init__(self, cliente, servicio, duracion):
        super().__init__()
        self.cliente, self.servicio, self.duracion = cliente, servicio, duracion
        self.estado = "CONFIRMADA"
        self.costo = 0

    def procesar(self, desc=0):
        try:
            self.costo = self.servicio.calcular_costo(self.duracion, desc)
            self.estado = "COMPLETADA"
            self.cliente.agregar_reserva(self)
            log_info(f"Reserva PROCESADA para {self.cliente.nombre} - Costo: ${self.costo}")
        except Exception as e:
            log_error(f"Error procesando reserva: {e}")
            raise ReservaError("No se pudo procesar") from e

    def describir(self):
        return f"Reserva {self._id}: {self.cliente.nombre} | {self.servicio.nombre} | Total: ${self.costo}"