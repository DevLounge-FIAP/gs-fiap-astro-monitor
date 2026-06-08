# regras.py
from modules.modulos import Missao_espacial
from rules.alertas import CentralDeAlertas

class MotorDeRegras:
    '''
    Sandbox isolado para lógicas booleanas, IFs e análises da missão.
    '''
    # INJEÇÃO DE DEPENDÊNCIA: O Motor recebe a missão e os alertas já prontos!
    def __init__(self, missao: Missao_espacial, central_alertas: CentralDeAlertas):
        self.missao = missao
        self.central_alertas = central_alertas

    def _registrar_evento_critico(self, mensagem: str, recomendacao: str):
        self.missao.registrar_evento_critico(f"[CRITICO] {mensagem} | {recomendacao}")

    def analisar_status_geral(self):

        #Adicionando os módulos, sistemas e sensores 
        mod_energia = self.missao.modulos.get('ENE-01')
        mod_suporte = self.missao.modulos.get('SUP-01')

        status_critico = False

        if mod_energia and mod_suporte:
            sistema_solar = mod_energia.sistemas.get('Solar-01').obter_geracao_atual()
            sistema_eolica = mod_energia.sistemas.get('Eolico-01').obter_geracao_atual()
            sistema_bateria = mod_energia.sistemas.get('Bateria-01').obter_geracao_atual()
            sensor_demanda = mod_energia.sensores.get('Sensor_Demanda_Total').obter_leitura_atual()
            sensor_radiacao = mod_suporte.sensores.get('Sensor_Radiacao').obter_leitura_atual()

            sensor_o2 = mod_suporte.sensores.get('Sensor_O2_Principal').obter_leitura_atual()
            sensor_temp_int = mod_suporte.sensores.get('Sensor_Temp_Int').obter_leitura_atual()
            sensor_integridade = mod_suporte.sensores.get("Sensor_Integridade").obter_leitura_atual()

            # ----- Regra 1 : Energia disponível -----
            # Verifica se a energia disponível é suficiente para suprir a demanda dos módulos, considerando bateria, solar e eólica 

            # -- Energia insuficiente --
            if sistema_bateria < 30 and (sistema_solar + sistema_eolica) < sensor_demanda: 
                self.central_alertas.enfileirar_alerta('CRITICO', 'Energia insuficiente', 'Desligar módulos não essenciais')
                self._registrar_evento_critico('Energia insuficiente', 'Desligar módulos não essenciais')
                status_critico = True

            # -- Risco de energia --
            elif sistema_bateria < 50 and (sistema_solar + sistema_eolica) < sensor_demanda: 
                self.central_alertas.enfileirar_alerta('ALERTA', 'Risco de energia ser insuficiente', 'Desligar módulos de baixa criticade')
                status_critico = True

            # ----- Regra 2 : Produção e armazenamento de energia -----
            # Verifica a produção solar cruzando com a radiação, a produção eólica e o nível da bateria, emitindo alertas conforme a criticidade de cada um

            # -- Paineis solares comprometidos --
            if sensor_radiacao > 1 and sistema_solar < 3000:
                self.central_alertas.enfileirar_alerta('CRITICO','Placas solares comprometidas','Verificar estado das placas solares')
                self._registrar_evento_critico('Placas solares comprometidas', 'Verificar estado das placas solares')
                status_critico = True

            # -- Paineis solares possivelmente comprometidos --
            elif sensor_radiacao > 1 and sistema_solar > 3000 and sistema_solar < 4000:
                self.central_alertas.enfileirar_alerta('ALERTA', 'Discrepância na produção de energia solar','Verificar estado das placas solares')
                status_critico = True

            # -- Sem produção de energia eólica -- 
            if not sistema_eolica: 
                self.central_alertas.enfileirar_alerta('ALERTA', 'Sem produção de energia eólica','Verifique integridade das turbinas eólicas') 
                status_critico = True

            # -- Armazenamento da bateria em baixo nível --
            if sistema_bateria < 50: 
                self.central_alertas.enfileirar_alerta('ALERTA','Bateria com baixo nível de energia', 'Considere economizar energia')
                status_critico = True

            # -- Armazenamento de energia da bateria zerado --
            if not sistema_bateria:
                self.central_alertas.enfileirar_alerta('ALERTA','Bateria zerada','Economize energia')
                status_critico = True


            # ----- Regra 3: Suporte à vida -----
            # Verifica se O2 e temperatura internas estão em níveis adequados por serem essenciais 

            if sensor_o2 < 19 and sensor_temp_int < 15:
                self.central_alertas.enfileirar_alerta('CRITICO','Risco a vida', 'Verificar módulo de suporte à vida urgente')
                self._registrar_evento_critico('Risco a vida', 'Verificar módulo de suporte à vida urgente')
                status_critico = True
            elif sensor_o2 < 19 or sensor_temp_int < 15:
                self.central_alertas.enfileirar_alerta('ALERTA','Risco a vida', 'Verificar módulo de suporte à vida')
                status_critico = True
            

            # ----- Regra 4: Integridade -----
            # Verifica o nível de integridade estrutural dos módulos e notifica de acordo com a deterioração 

            if not sensor_integridade:
                self.central_alertas.enfileirar_alerta('CRITICO','Integridade zerada','Módulo destruído') 
                self._registrar_evento_critico('Integridade zerada', 'Módulo destruído')
                status_critico = True
            elif sensor_integridade < 70 and sensor_integridade > 0:
                self.central_alertas.enfileirar_alerta('CRITICO','Integridade extremamente comprometida','Enviar reparo')
                self._registrar_evento_critico('Integridade extremamente comprometida', 'Enviar reparo')
                status_critico = True
            elif sensor_integridade < 90 and sensor_integridade > 0: 
                self.central_alertas.enfileirar_alerta('ALERTA', 'Integridade afetada', 'Verificar integridade dos módulos')
                status_critico = True
            

            # ----- Regra 5: Módulos estáveis -----
            # Verifica se todos os parâmetros estão dentro dos níveis normais
            if not status_critico and sistema_bateria > 80 and (sistema_solar + sistema_eolica) > sensor_demanda and sensor_o2 > 18 and sensor_temp_int > 20:
                self.central_alertas.enfileirar_alerta('NORMAL','Módulos estáveis','Sistemas e sensores indicam normalidades')

            # ----- Regra 6: Inconsistência Proposital -----
            if sensor_temp_int > 1000 or sistema_bateria < 0:
                self.central_alertas.enfileirar_alerta('CRITICO','Falha de sensor detectada','Reiniciar sensores do módulo')

        pass 

    def executar_previsao_tendencia(self):
        '''
        Método reservado para puxar a matriz e fazer o cálculo. aqui é para a Madu
        '''
        # matriz_dados = self.missao.gerar_matriz_telemetria()
        pass
