from modules import modulos

class CentraldDeAlertas(modulos.Missao_espacial):
    fila_alertas = []
    def enfileirar_alerta(self,prioridade, mensagem):
        self.prioridade = prioridade
        self.mensagem = mensagem

class MotorDeRegras(Sistema, CentralDeAlertas):

    def __init__(self, missao, central_alerta):
        self.missao= missao
        self.central_alertas= central_alerta