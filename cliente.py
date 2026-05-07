@property
def email(self):
    return self.__email

@email.setter
def email(self, valor):
    if "@" not in valor:
        raise ValidationError(f"Email inválido: {valor}")
    self.__email = valor

def obtener_detalles(self):
    return f"Cliente: {self.__nombre} | ID: {self._id_entidad}"
