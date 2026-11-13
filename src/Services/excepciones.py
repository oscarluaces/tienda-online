'''Excepciones de negocio de la tienda.

TiendaService las lanza y main.py las traduce a códigos HTTP,
de modo que la lógica de negocio no depende de FastAPI.
'''


class TiendaError(Exception):
    '''Error genérico de la tienda.'''


class RecursoNoEncontrado(TiendaError):
    '''El usuario o producto no existe (HTTP 404).'''


class Conflicto(TiendaError):
    '''Choca con el estado actual, p. ej. email ya registrado (HTTP 409).'''


class OperacionNoValida(TiendaError):
    '''No se puede realizar, p. ej. stock insuficiente o el usuario no es cliente (HTTP 400).'''
