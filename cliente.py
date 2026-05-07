import re # Librería para validaciones de texto complejas (Regex)
from abc import ABC, abstractmethod

# --- EXCEPCIÓN PERSONALIZADA PARA VALIDACIONES ---
class ValidationError(Exception):
    """Se lanza cuando un dato personal no cumple con los requisitos de seguridad."""
    pass

# --- CLASE ABSTRACTA PADRE ---
class EntidadBase(ABC):
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad # Atributo Protegido (Encapsulación nivel 1)

    @abstractmethod
    def mostrar_informacion(self):
        pass

# --- CLASE CLIENTE ROBUSTA ---
class Cliente(EntidadBase):
    def __init__(self, id_cliente, nombre, email, telefono):
        super().__init__(id_cliente)
        # Usamos los setters para que la validación se ejecute desde el primer segundo
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    # --- ENCAPSULACIÓN DEL NOMBRE ---
    @property
    def nombre(self):
        return self.__nombre # Atributo Privado (Encapsulación nivel 2)

    @nombre.setter
    def nombre(self, valor):
        # Validación: No vacío y mínimo 3 caracteres
        if not valor or len(valor.strip()) < 3:
            raise ValidationError(f"Nombre inválido: '{valor}'. Debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    # --- ENCAPSULACIÓN DEL EMAIL (Validación con Regex) ---
    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        # Expresión regular para validar un correo electrónico estándar
        patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(patron, valor):
            raise ValidationError(f"Correo electrónico inválido: '{valor}'.")
        self.__email = valor.lower()

    # --- ENCAPSULACIÓN DEL TELÉFONO ---
    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        # Validación: Solo números y longitud entre 7 y 15 dígitos
        if not str(valor).isdigit() or not (7 <= len(str(valor)) <= 15):
            raise ValidationError(f"Teléfono inválido: '{valor}'. Debe contener solo números (7-15 dígitos).")
        self.__telefono = valor

    # Implementación obligatoria del método abstracto
    def mostrar_informacion(self):
        return f"ID: {self._id_entidad} | Cliente: {self.__nombre} | Email: {self.__email} | Tel: {self.__telefono}"

# --- PRUEBA DE ROBUSTEZ (Ejemplos de uso) ---

print("--- Iniciando validaciones del sistema ---")

try:
    # 1. Intento de crear un cliente válido
    cliente1 = Cliente(1, "Carlos Gomez", "carlos@gmail.com", "3001234567")
    print(f"ÉXITO: {cliente1.mostrar_informacion()}")

    # 2. Intento de modificar el email con un dato erróneo después de creado
    print("\nIntentando cambiar email a uno inválido...")
    cliente1.email = "correo_falso.com" 

except ValidationError as e:
    print(f"ERROR DETECTADO: {e}")

try:
    # 3. Intento de crear un cliente con nombre muy corto o vacío
    print("\nIntentando crear cliente con nombre inválido...")
    cliente2 = Cliente(2, "Jo", "jo@p.com", "1234567")
except ValidationError as e:
    print(f"ERROR DETECTADO: {e}")

try:
    # 4. Intento de crear un cliente con teléfono que contiene letras
    print("\nIntentando crear cliente con teléfono alfanumérico...")
    cliente3 = Cliente(3, "Maria Perez", "maria@p.com", "300-CALL-ME")
except ValidationError as e:
    print(f"ERROR DETECTADO: {e}")
