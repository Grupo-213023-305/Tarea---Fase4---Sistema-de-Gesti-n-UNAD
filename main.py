# ============================================================
# SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ
# Integración: Santiago Bernal Pertuz + Colaboradora
# Multimedia Engineering - UNAD 2026
# ============================================================

import re
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime

# ============================================================
# CONFIGURACIÓN DE LOGS Y EXCEPCIONES
# ============================================================
logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def log_info(mensaje): logging.info(mensaje)
def log_error(mensaje): logging.error(mensaje)

class ClienteError(Exception): pass
class ServicioError(Exception): pass
class ReservaError(Exception): pass
class No_disponible(Exception): pass
class Registro_error(Exception): pass

# ============================================================
# CLASES BASE (ABSTRACCIÓN)
# ============================================================

class Servicio(ABC):
    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        pass

class Entidad(ABC):
    def __init__(self):
        self._id = str(uuid.uuid4())[:8]
        self._fecha_creacion = datetime.now()

    @abstractmethod
    def describir(self):
        pass

# ============================================================
# MÓDULO 1: GESTIÓN DE INVENTARIO Y ALQUILER (Santiago Bernal)
# ============================================================

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

    def cambiar_perifericos(self, estado):
        self.__perifericos = estado

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
        print ("Límite: 4h. Recargo tardío: $5000")
        print (f"{'ID':<8} | {'Tipo':<12} | {'gama':<8} | {'Estado' :<12}")
        print ("-" * 50)
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
            if equipo.prestado(): raise No_disponible(f"Ya alquilado.")
            if not (0 <= int(i_hora) <= 23): raise Registro_error("Hora inválida.")
            equipo.estado(True, i_hora)
            return "Alquiler registrado con éxito"
        except Exception as e:
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
            return f"Recibo: ID {id_buscado} | Total: ${total} {'(Con Recargo)' if recargo > 0 else ''}"
        except Exception as e:
            return f"Error: {e}"

# ============================================================
# MÓDULO 2: GESTIÓN DE CLIENTES Y RESERVAS 
# ============================================================

class Cliente(Entidad):
    patron_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    def __init__(self, nombre, email, telefono):
        super().__init__()
        self._historial = []
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    @property
    def nombre(self): return self._nombre
    @nombre.setter
    def nombre(self, v):
        if not v or len(v.strip()) < 3: raise ClienteError("Nombre inválido")
        self._nombre = v.strip().title()

    @property
    def email(self): return self._email
    @email.setter
    def email(self, v):
        if not re.match(self.patron_email, v): raise ClienteError("Email inválido")
        self._email = v.lower()

    @property
    def telefono(self): return self._telefono
    @telefono.setter
    def telefono(self, v):
        if not re.fullmatch(r"\d{7,15}", str(v)): raise ClienteError("Teléfono inválido")
        self._telefono = str(v)

    def agregar_reserva(self, reserva): self._historial.append(reserva)
    def describir(self): return f"Cliente: {self.nombre} | IDs: {len(self._historial)}"

class ServicioHeredado(Servicio):
    def __init__(self, nombre, tarifa):
        if tarifa <= 0: raise ServicioError("Tarifa inválida")
        self.nombre = nombre
        self.tarifa = tarifa
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
        self.costo = self.servicio.calcular_costo(self.duracion, desc)
        self.estado = "COMPLETADA"
        self.cliente.agregar_reserva(self)

    def describir(self):
        return f"Reserva {self._id}: {self.cliente.nombre} | {self.servicio.nombre} | Total: ${self.costo}"

# ============================================================
# MENÚ PRINCIPAL INTEGRADO
# ============================================================

def menu_alquiler_santiago(gestion_inst):
    while True:
        print("\n--- MÓDULO ALQUILER DE EQUIPOS ---")
        print("1. Ver Inventario\n2. Alquilar\n3. Devolver\n4. Volver")
        op = input("Seleccione: ")
        if op == "1": gestion_inst.mostrar_inventario()
        elif op == "2":
            num = input("Número de equipo (001-010): ")
            h = input("Hora inicio (0-23): ")
            print(gestion_inst.Alquiler(num, h))
        elif op == "3":
            num = input("Número de equipo: ")
            h = input("Hora entrega: ")
            print(gestion_inst.Devolucion(num, h))
        elif op == "4": break

def menu_reservas_companera():
    # Mini-sistema para el módulo de la compañera
    print("\n--- MÓDULO RESERVAS DE SALAS/ASESORÍAS ---")
    try:
        nom = input("Nombre Cliente: ")
        mail = input("Email: ")
        tel = input("Teléfono: ")
        c = Cliente(nom, mail, tel)
        
        print("1. Sala VIP ($50k/h)\n2. Asesoría Python ($70k/h)")
        serv_op = input("Servicio: ")
        s = ServicioSala("Sala VIP", 50000) if serv_op == "1" else ServicioAsesoria("Asesoría Python", 70000)
        
        dur = float(input("Duración (horas): "))
        r = Reserva(c, s, dur)
        r.procesar(0.1) # 10% descuento por defecto
        print("\n" + r.describir())
        log_info(f"Reserva creada para {nom}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    gestion_santiago = Gestion()
    
    while True:
        print("\n================================")
        print("   SISTEMA INTEGRAL SOFTWARE FJ")
        print("================================")
        print("1. Gestionar Alquiler de Equipos")
        print("2. Gestionar Reservas y Clientes")
        print("3. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            menu_alquiler_santiago(gestion_santiago)
        elif opcion == "2":
            menu_reservas_companera()
        elif opcion == "3":
            print("Cerrando sistema...")
            break
        else:
            print("Opción no válida.")
