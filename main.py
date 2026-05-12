# ============================================================
# SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ
# ============================================================

import re
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime

# CONFIGURACIÓN DE LOGS 
# ------------------------------------------------------------
logger = logging.getLogger("SoftwareFJ")
logger.setLevel(logging.INFO)

# Creamos el manejador del archivo con encoding utf-8
file_handler = logging.FileHandler("logs.txt", encoding="utf-8", delay=False)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log_info(mensaje): logger.info(mensaje)
def log_error(mensaje): logger.error(mensaje)

# EXCEPCIONES PERSONALIZADAS [Criterio 1: Nivel Alto]
class ClienteError(Exception): pass
class ServicioError(Exception): pass
class ReservaError(Exception): pass
class No_disponible(Exception): pass
class Registro_error(Exception): pass

# CLASES BASE
class Servicio(ABC):
    @abstractmethod
    def calcular_costo(self, *args, **kwargs): pass

class Entidad(ABC):
    def __init__(self):
        self._id = str(uuid.uuid4())[:8]
        self._fecha_creacion = datetime.now()
    @abstractmethod
    def describir(self): pass

# --- MÓDULO ALQUILER (Santiago Bernal) ---
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

class Gestion(Servicio):
    def __init__(self):
        self.__inventario = []
        self._cargar_inventario_i()

    def _cargar_inventario_i(self):
        for i in range (1,11):
            id_eq = f"EQ-{i:03}"
            if i <= 3: nuevo = Portatil(id_eq, "Alta")
            elif i <= 7: nuevo = All_in_One(id_eq, "Media")
            else: nuevo = Tablet(id_eq, "Baja")
            self.__inventario.append(nuevo)

    def mostrar_inventario(self):
        print ("\n--- Inventario Disponible ---")
        print (f"{'ID':<8} | {'Tipo':<12} | {'gama':<8} | {'Estado' :<12}")
        for equipo in self.__inventario:
            est = "Ocupado" if equipo.prestado() else "Disponible"
            print (f"{equipo.obtener_id():<8} | {equipo.tipo:<12} | {equipo.obtener_gama():<8} | {est:<12}")

    def calcular_costo(self, gama, horas, perifericos, descuento=0):
        precios = {"Baja": 2000, "Media": 5000, "Alta": 10000}
        p_hora = precios.get(gama, 0)
        if perifericos: p_hora += 1500
        total = (p_hora * horas)
        return int(total - (total * (descuento / 100)))

    def buscar_equipo(self, id_buscado):
        for eq in self.__inventario:
            if eq.obtener_id() == id_buscado: return eq
        raise Registro_error(f"El equipo {id_buscado} no existe.")

    def Alquiler(self, num, i_hora):
        try:
            id_buscado = f"EQ-{str(num).zfill(3)}"
            equipo = self.buscar_equipo(id_buscado)
            if equipo.prestado(): raise No_disponible(f"Equipo {id_buscado} ya ocupado.")
            if not (0 <= int(i_hora) <= 23): raise Registro_error("Hora fuera de rango.")
            equipo.estado(True, i_hora)
            log_info(f"Alquiler EXITOSO: {id_buscado} a las {i_hora}:00")
            return "Alquiler registrado con éxito"
        except Exception as e:
            log_error(f"Fallo en Alquiler: {e}")
            return f"Atención: {e}"

    def Devolucion(self, num, h_entrega, descuento=0):
        try:
            id_buscado = f"EQ-{str(num).zfill(3)}"
            equipo = self.buscar_equipo(id_buscado)
            if not equipo.prestado(): raise Registro_error("No estaba alquilado.")
            tiempo = int(h_entrega) - int(equipo.obtener_h_alquiler())
            if tiempo <= 0: raise Registro_error("Hora de entrega inválida.")
            
            recargo = 5000 if tiempo > 4 else 0
            total = self.calcular_costo(equipo.obtener_gama(), tiempo, equipo.tiene_perifericos(), descuento) + recargo
            equipo.estado(False, None)
            log_info(f"Devolución EXITOSA: {id_buscado}. Total: ${total}")
            return f"Recibo: ID {id_buscado} | Total: ${total} {'(Con Recargo)' if recargo > 0 else ''}"
        except Exception as e:
            log_error(f"Fallo en Devolución: {e}")
            return f"Error: {e}"

# --- MÓDULO RESERVAS (Colaboradora) ---
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

# MENÚ PRINCIPAL
if __name__ == "__main__":
    gestion_santiago = Gestion()
    while True:
        print("\n=== SOFTWARE FJ - MENÚ INTEGRADO ===")
        print("1. Alquiler de Equipos \n2. Reservas de Salas \n3. Salir")
        op = input("Selección: ")
        
        if op == "1":
            while True:
                print("\n-- MÓDULO ALQUILER --")
                print("1. Ver Inventario\n2. Alquilar\n3. Devolver\n4. Volver")
                sub = input("Opción: ")
                if sub == "1": gestion_santiago.mostrar_inventario()
                elif sub == "2":
                    num = input("Número equipo (ej: 1): ")
                    h = input("Hora (0-23): ")
                    print(gestion_santiago.Alquiler(num, h))
                elif sub == "3":
                    num = input("Número equipo: ")
                    h = input("Hora entrega: ")
                    print(gestion_santiago.Devolucion(num, h))
                elif sub == "4": break
        
        elif op == "2":
            print("\n-- MÓDULO RESERVAS --")
            try:
                nom = input("Nombre: "); mail = input("Email: "); tel = input("Tel: ")
                c = Cliente(nom, mail, tel)
                print("1. Sala VIP\n2. Asesoría")
                s = ServicioSala("Sala VIP", 50000) if input("Op: ") == "1" else ServicioAsesoria("Asesoría", 70000)
                dur = float(input("Duración: "))
                r = Reserva(c, s, dur)
                r.procesar(0.1)
                print(r.describir())
            except Exception as e:
                log_error(f"Error en Módulo Reservas: {e}")
                print(f"Error: {e}")

        elif op == "3":
            print("Cerrando sistema. Revisar logs.txt."); break
