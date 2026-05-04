# Software FJ
#Santiago Bernal Pertuz 
#Programación
#Se requiere agregar la clase principal "Servicio para que el código este completo"
#..........Alquiler de equipos..........
#Importamos abc para crear clases abstractas 
#abstractmethod es un decorador que hace que las clases hijas  implementes métodos
from abc import ABC, abstractmethod
class Servicio(ABC):
    @abstractmethod
    def calcular_costo(self, gama, horas, perifericos):
        pass
class Gestion(Servicio):
    def __init__(self):
#Creamos una lista para almacenar los equipos del inventario
        self.__inventario = []
        self._cargar_inventario_i()
    def mostrar_inventario(self):
        print ("\n Inventario Disponible")
        print ("Tiempo máximo de alquiler 4 horas. Recargo por entrega tardía $5000")
#Alineación de la tabla del inventario
        print (f"{'ID':<8} | {'Tipo':<12} | {'gama':<8} | {'Estado' :<12}")
#Separar inventario
        print ("-" * 50)
        for equipo in self.__inventario: 
            estado = "Ocupado" if equipo.prestado() else "Disponible"
            gama = equipo.obtener_gama()
            print (f"{equipo.obtener_id():<8} | {equipo.tipo:<12} | {gama:<8} | {estado:<12}")
    def _cargar_inventario_i(self):
#Genera 10 códigos de equipos para el inventario
        for i in range (1,11):
            id_eq = f"EQ-{i:03}"
            if i <= 3:
                nuevo = Portatil(id_eq, "Alta")
            elif i <= 7:
                nuevo = All_in_One(id_eq, "Media")
            else: 
                nuevo = Tablet(id_eq, "Baja")
            self.__inventario.append (nuevo)
    def calcular_costo(self, gama, horas, perifericos, descuento = 0):
    #Precios base
            precios_base = {
                "Baja": 2000,
                "Media": 5000,
                "Alta": 10000
            }
    #Obtener precio del alquiler
            precio_hora = precios_base.get(gama, 0)
    #Agregar precio de perifericos adicionales
            if perifericos:
                precio_hora += 1500
            total_sin_descuento = precio_hora * horas
            total_final = total_sin_descuento - (total_sin_descuento * (descuento / 100))
            return int (total_final)
    def mostrar_detalle(self):
            return "Servicio de Alquiler de Dispositivos"
    def buscar_equipo (self, id_buscado):
#Busca información del equipo solicitado, como la id o el estado de prestamo
        for equipo in self.__inventario:
            if equipo.obtener_id() == id_buscado:
                return equipo
        raise Registro_error(f"El equipo {id_buscado} no existe.")
    def Alquiler(self, id_buscado, i_hora):
        try:
#Auto completa La ID del equipo si el usuario no lo escribe completo Ej: 1 = 001
            id_buscado = f"EQ-{str(id_buscado).zfill(3)}"
#Buscar equipo
            equipo = self.buscar_equipo(id_buscado)
#Validar disponibilidad del equipo
            if equipo.prestado():
                raise No_disponible(f"El equipo {id_buscado} ya fue alquilado.")
#Validar hora de alquiler
            if int(i_hora) < 0 or int (i_hora) > 23:
                raise Registro_error("La hora ingresada no es válida (0-23).")
            equipo.estado(True, i_hora)
            return "Alquiler registrado con éxito"
        except No_disponible as e:
            self.registrar_en_log(f"Error: {e}")
            return f"Error: Equipo no disponible."
        except Registro_error as e:
            self.registrar_en_log(f"Error de registro: {e}")
            return f"Atención: {e}"
        except ValueError:
            return "Error: Formato de hora incorrecto."
        finally:
            print("Alquiler finalizado")
#Registrar log
    def registrar_en_log(self, mensaje):
        try:
            archivo = open("log_alquileres.txt", "a")
            archivo.write(f"{mensaje}\n")
        except Exception as e:
            print(f"No se pudo escribir el log: {e}")
        finally:
            archivo.close()
    def Devolucion(self, id_buscado, h_entrega, descuento=0):
        try: 
#Buscar equipos
            equipo = self.buscar_equipo(id_buscado)
#Validamos el prestamo
            if not equipo.prestado():
                raise Registro_error(f"El equipo {id_buscado} no no ha sido alquilado.")
#Calcular el tiempo
            h_inicio = int(equipo.obtener_h_alquiler())
            tiempo_uso = int(h_entrega) - h_inicio
# Validación de hora
            if tiempo_uso <=0:
                raise Registro_error("La hora de entrega no puede ser menor o igual a la de inicio.")
            limite_horas = 4
            recargo = 0
            mensaje_tardia =""
            if tiempo_uso > limite_horas:
                recargo = 5000
                mensaje_tardia = f"\n Entrega tardía. Costo adicional ${recargo}"
            total_pagar = self.calcular_costo(equipo.obtener_gama(), tiempo_uso, equipo.tiene_perifericos(), descuento)
            total_final = total_pagar + recargo
            equipo.estado(False, None)
#Factura
            return (f"Recibo de Pago \n ID: {id_buscado} \n Tiempo de uso: {tiempo_uso} hora(s) \n Descuento: {descuento}% \n {mensaje_tardia} \n Total: ${total_final}")
        except Registro_error as e: 
            self.registrar_en_log(f"Error cobro {e}")
            return f"Error en dovolución: {e}"
        except ValueError:
            return "Error: La hora debe ser un número entero."
#Cierre del proceso
        finally:
            print(f"Cierre de proceso para el equipo {id_buscado}")
class Equipo:
#Definir los atributos privados de la clase Equipo
    def __init__(self, id_equipo, gama, perifericos):
        self.__id_equipo = id_equipo
        self.__gama = gama
        self.__perifericos = perifericos
        self.__prestado = False
        self.__h_alquiler = None
#Obtener información del equipo
    def obtener_gama(self):
        return self.__gama
    def tiene_perifericos(self):
        return self.__perifericos
    def obtener_id(self):
        return self.__id_equipo
    def prestado(self):
        return self.__prestado
    def obtener_h_alquiler(self):
        return self.__h_alquiler
#Cambiar estado del equipo    
    def estado(self, estado, hora=None):
        self.__prestado = estado
        self.__h_alquiler = hora
#Elegir perifericos 
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
#Excepciones 
class No_disponible(Exception):
    pass
class Registro_error(Exception):
    pass
class Lista(Servicio):
    def __init__(self):
        self.__inventario = []
#Agrega equipos a la lista
    def agregar_equipo(self, equipo):
        self.__inventario.append(equipo)
#Busca equipos en la lista
    def buscar_equipo(self, id_buscado):
        for equipo in self.__inventario:
            if equipo.obtener_id() == id_buscado:
                return equipo
#Error causado si no esta el equipo en el inventario
        raise Registro_error(f"El equipo con ID {id_buscado} no existe.")
#..........Menu..........
#Creación de menu para alquiler, devolución y cobro de equipos
if __name__ == "__main__":
    sistema = Gestion()
#Opciones del alquiler de equipos
    while True:
        print (sistema.mostrar_detalle())
        print ("1. Registrar Alquiler")
        print ("2. Registrar Devolución y Generar Factura")
        print ("3. Salir")
#Selección de una opción
        opcion = input ("Seleccione una opción: ")
        if opcion == "1":
            sistema.mostrar_inventario()
            num = input ("\n Ingrese unicamente el número del equipo: ")
            id_temp = f"EQ-{num.zfill(3)}"
            try:
                equipo_obj = sistema.buscar_equipo(id_temp)
                if equipo_obj.tipo != "All in One":
                    resp = input("¿Desea incluir perifericos adicionales? (+$1500) s/n: ").lower()
                    equipo_obj.cambiar_perifericos(True if resp == 's' else False)
                hora = input ("Ingrese hora del alquiler (0-23): ")
                print (f"\n Resultado: {sistema.Alquiler(num, hora)}")
            except Registro_error as e:
                print(f"\n Error {e}")
        elif opcion == "2":
            num = input ("Ingrese unicamente el número del equipo a devolver: ")
            hora_e = input ("Ingrese hora de entrega (0-23): ")
            valor_desc = 0
            pregunta_desc = input("¿Desea aplicar un descuento s/n: ").lower()
            if pregunta_desc == 's': 
                valor_desc = int(input("Ingrese el porcentaje de descuento: "))
            n_id = f"EQ-{str(num).zfill(3)}"
            print (f"\n {sistema.Devolucion(n_id, hora_e, valor_desc)}")
        elif opcion == "3":
            print ("Saliendo del sistema")
            break
        else: 
            print ("Opción no válida, intenta nuevamente.")
