# regras.py
from modules.modulos import Missao_espacial
from alertas import CentralDeAlertas

class MotorDeRegras:
    '''
    Sandbox isolado para lógicas booleanas, IFs e análises da missão.
    '''
    # INJEÇÃO DE DEPENDÊNCIA: O Motor recebe a missão e os alertas já prontos!
    def __init__(self, missao: Missao_espacial, central_alertas: CentralDeAlertas):
        self.missao = missao
        self.central_alertas = central_alertas

    def analisar_status_geral(self):
        '''
        Método onde deve ser criado as lógicas condicionais (IF/ELIF/ELSE).
        '''
        # EXEMPLO PARA A MICHELLY DE COMO DEVE USAR:
        
        # 1. Pega o módulo de suporte (exemplo)
        # mod_suporte = self.missao.modulos.get('SUP-01')
        # if mod_suporte:
        #     sensor_temp = mod_suporte.sensores.get('Sensor_Temp_Int')
        #     if sensor_temp:
        #         temp_atual = sensor_temp.obter_leitura_atual()
        #         
        #         # 2. Faz a regra:
        #         if temp_atual < 18.0:
        #             # 3. Chamar a Central de Alertas pronta:
        #             self.central_alertas.enfileirar_alerta('CRITICO', 'Temperatura caindo!', 'Ligar aquecedor')
        pass 

    def executar_previsao_tendencia(self):
        '''
        Método reservado para puxar a matriz e fazer o cálculo. aqui é para a Madu
        '''
        # matriz_dados = self.missao.gerar_matriz_telemetria()
        pass