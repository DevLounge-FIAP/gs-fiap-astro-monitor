from modules import modulos

class CentraldDeAlertas(modulos.Missao_espacial):
    fila_alertas = []
    def enfileirar_alerta(self,prioridade, mensagem):
        self.prioridade = prioridade
        self.mensagem = mensagem

