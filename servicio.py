from abc import ABC, abstractmethod

# CLASES BASE
class Servicio(ABC):
    @abstractmethod
    def calcular_costo(self, *args, **kwargs): pass

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

# --- TIPOS DE EQUIPO (MÓDULO ALQUILER) ---
class Equipo:
    def __init__(self, id_equipo, gama, perifericos):
        self.__id_equipo = id_equipo
        self.__gama = gama
        self.__perifericos = perifericos
        self.__prestado = False
        self.__h_alquiler = None
    def obtener_gama(self): return self.__gama
    def tiene_perifericos(self): return self.__perifericos
    def obtener_id(self): return self.__id_equipo
    def prestado(self): return self.__prestado
    def obtener_h_alquiler(self): return self.__h_alquiler
    def estado(self, estado, hora=None):
        self.__prestado = estado
        self.__h_alquiler = hora
    def cambiar_perifericos(self, estado): self.__perifericos = estado

class Portatil(Equipo):
    def __init__(self, id_equipo, gama):
        super().__init__(id_equipo, gama, False)
        self.tipo = "Portatil"

class All_in_One(Equipo):
    def __init__(self, id_equipo, gama):
        super().__init__(id_equipo, gama, True)
        self.tipo = "All in One"

class Tablet(Equipo):
    def __init__(self, id_equipo, gama):
        super().__init__(id_equipo, gama, False)
        self.tipo = "Tablet"
