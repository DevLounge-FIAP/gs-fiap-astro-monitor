
#-----------------Classe Pai-----------------#
class Missao_espacial:
    '''
    Parte central da missão. Agrega todos os módulos e sistemas.
    '''
    def __init__(self):
        #Dic(Tabela Hash) pra garantintir acesso O(1) em vez de lista que usava for psts acessar.
        self.modulos = {}
        #Pilha de eventos, um entra em cima do outro no log  (LIFO)
        self.log_eventos_criticos = []

    def adicionar_modulo(self, modulo):
        '''Método para inserir um módulo no dicionário.
        Ele pega 'id_nome' do obejto e a transforma na Chave.
        '''
        self.modulos[modulo.id_nome] = modulo
        print(f"Módulo {modulo.id_nome} ({modulo.tipo} adicionado!!)")

    def registrar_evento_critico(self, evento: str):
        '''
        Faz o PUSH (inserção no topo) de um evento na pilha (LIFO)
        '''
        self.log_eventos_criticos.append(evento)

    def obter_ultimo_evento(self):
        '''
        Exibe qual foi o último evento crítico sem removê-lo da pilha.
        '''
        if len(self.log_eventos_criticos) > 0:
            return self.log_eventos_criticos[-1] # -1 é sempre o índice do último elemento adicionado a pilha.
        return "Nenhum evento crítico registrado." #Esse é o else caso não tenha evento na pilha.
    
    def alterar_status_modulo(self, id_modulo: str, novo_status: bool, motivo: str):
        '''
        Método para alterar o status do modulo e registrar na pilha de Log (registrar_evento_critico).
        '''
        if id_modulo in self.modulos:

            modulo_alvo = self.modulos[id_modulo]
            modulo_alvo.alterar_status(novo_status)

            status_str = "LIGADO" if novo_status else "DESLIGADO"
            evento_formatado = f"[ALERTA] Módulo {id_modulo} altera para {status_str}. Motivo: {motivo}"

            self.registrar_evento_critico(evento_formatado)
            print(evento_formatado)

        else:
            print(f"Erro: Módulo com ID '{id_modulo} não encontrado na missão")

    def gerar_matriz_telemetria(self) -> list:
        '''
        Gera uma matriz sem numpy, logo é uma lista de listas, junta todos os dados temporais coletados pelos sensores.
        Essa matriz deve ser consumida para a análise preditiva.
        '''
        matriz = []
        cabecalho = ['Sol']
        matriz.append(cabecalho)

        modulo_alvo = self.modulos.get('ENE-01')
        if modulo_alvo is None:
            return matriz   #Retorna so o cabeçalho se o módulo não existir.
        
        sistema_alvo = modulo_alvo.sistemas.get('Solar-01')
        if sistema_alvo is None:
            return matriz

        tamanho_historico = len(sistema_alvo.historico_geracao)

        print(f"DEBUG: O histórico tem {tamanho_historico} linhas.")


        return matriz

#-----------------Modulos-----------------#
class Modulo:
    '''
    Representação de um módulo físico da missão,
    '''
    def __init__(self,id_nome: str, tipo: str, funcao: str, criticidade: int, consumo: int):
        '''
        Args:
            id_nome: Identificador único (ex: 'SUP-01')
            tipo: Categoria do módulo ('Modulo Suporte à vida',' Módulo Energético', 'Módulo Laboratório', 'Modulo Armazenamento',
            'Modulo Habitat', Modulo Comunicação)
            funcao: Descrição da função ('Suporte à Vida', 'Pesquisa', 'Controle de Energia')
            criticidade: 1 (pouco essencial) a 5 (insubstituível)
            consumo: Energia consumida por hora (valor absoluto)
        '''
        self.id_nome = id_nome
        self.tipo = tipo
        self.funcao = funcao
        self.criticidade = criticidade
        self.consumo = consumo
        self.status = True #Modulo inicia ligado
        #Chave é o nome e valor o proprio sistema.
        self.sistemas = {}
        self.sensores = {}

    def adicionar_sistema(self, sistema):
        '''Junta um sistema a esse módulo. '''
        self.sistemas[sistema.nome] = sistema

    def adicionar_sensor(self, sensor):
        '''Junta um sensor ao módulo'''
        self.sensores[sensor.nome] = sensor

    def alterar_status(self, novo_status: bool):
        '''Visualizar status'''
        self.status = novo_status   


#-----------------Sistemas-----------------#
class Sistema:
    '''Classe que representa os sistemas, tanto de geração quanto armazenamento'''
    def __init__(self, nome: str, capacidade_max_geracao: int, geracao_atual: float, consumo: float ,capacidade_max_armazenamento: int):
        '''
        Args:
            nome: Nome do Sistema.
            capacidade_max: Capacidade maxima de geração do sistema.
            geracao_atual: Geração atual.
            capacidade_max_armazenamento: Capacidade maxima de armazenamento do sistema.
        '''
        self.nome = nome
        self.capacidade_max_geracao = capacidade_max_geracao
        self.capacidade_max_armazenamento = capacidade_max_armazenamento
        self.historico_geracao = [geracao_atual]
        self.historico_consumo = [consumo]

    def atualizar_dados(self, nova_geracao: float, novo_consumo: float):
        '''
        Faz o APPEND do novo dado para ter um histórico.
        '''
        self.historico_geracao.append(nova_geracao)
        self.historico_consumo.append(novo_consumo)
        if len(self.historico_geracao) > 100:
            self.historico_geracao.pop(0)
        if len(self.historico_consumo) > 100:
            self.historico_consumo.pop(0)

    def obter_geracao_atual(self) -> float:
        '''
        Retorna sempre o último dado adicionado na lista de geracao
        '''
        return self.historico_geracao[-1]

    def obter_consumo_atual(self) -> float:
        '''
        Retorna sempre o último dado adicionado na lista de consumo.
        '''
        return self.historico_consumo[-1]

class SistemaGeracaoSolar(Sistema):
    '''Painéis Solares.'''
    def __init__(self, nome: str, capacidade_max_geracao: int, geracao_atual: int):
        super().__init__(nome, capacidade_max_geracao, geracao_atual,consumo = 0, capacidade_max_armazenamento = 0)

class SistemaGeracaoEolica(Sistema):
    '''Turbinas Eolicas.'''
    def __init__(self, nome: str, capacidade_max_geracao: int, geracao_atual: int):
        super().__init__(nome, capacidade_max_geracao, geracao_atual,consumo = 0, capacidade_max_armazenamento = 0)

class SistemaArmazenamentoEnergetico(Sistema):
    '''Sistema de baterias.'''
    def __init__(self, nome: str, capacidade_max_armazenamento: int = 100):
        super().__init__(nome, capacidade_max_geracao = 0, geracao_atual=0,consumo = 0, capacidade_max_armazenamento=capacidade_max_armazenamento)

#-----------------Sensores-----------------#
class Sensores: 
    '''Classe para representar os sensores da missão.'''
    def __init__(self, nome: str, tipo: str, funcao: str, unidade: str):
        '''
        Args:
            nome: Nome do sensor.
            tipo: Categoria do sensor (Sensor de Temperatura, Sensor de Pressão, Sensor de Umidade, Sensor de Radiação, Sensor de Movimento)
            funcao: Descrição da função do sensor.

            unidade: Unidade da leitura (°C, hPa, %, mSv/h, m/s²)
        '''
        self.nome = nome
        self.tipo = tipo
        self.funcao = funcao
        self.leitura = []
        self.unidade = unidade

    def registrar_leitura(self,valor):
        self.leitura.append(valor)      

class SensorIrradiacao(Sensores):
    
    def __init__(self, nome: str, funcao: str, unidade: str):
        super().__init__(
            nome=nome,
            tipo="Sensor de Irradiação Solar",
            funcao=funcao,
            unidade=unidade,
        )      

class SensorVelocidadeVento(Sensores):
    
    def __init__(self, nome: str, funcao: str, unidade: str):
        super().__init__(
            nome=nome,
            tipo="Sensor de Velocidade do Vento",
            funcao=funcao,
            unidade=unidade,
        ) 

class SensorNivelEnergia(Sensores):
   
    def __init__(self, nome: str, funcao: str, unidade: str):
        super().__init__(
            nome=nome,
            tipo="Sensor da Bateria",
            funcao=funcao,
            unidade=unidade,
        ) 
"""*Criação dos Sensores do Módulo Energético*"""

class SensorO2(Sensores):
    
   def __init__(self, nome: str, funcao: str, unidade: str):  
        super().__init__(
            nome=nome,
            tipo="Sensor do Oxigênio",
            funcao=funcao,
            unidade=unidade,
        ) 

class SensorTemperaturaInterna(Sensores):
    
    def __init__(self, nome: str, funcao: str,  unidade: str): 
        super().__init__(
            nome=nome,
            tipo="Sensor da Temperatura Interna",
            funcao=funcao,
            unidade=unidade,
        ) 
"""*Criação dos Sensores do Módulo Suporte a Vida*"""

class SensorQualidadeSinal(Sensores):
    
    def __init__ (self, nome: str, funcao: str, unidade: str):
        super().__init__(
            nome=nome,
            tipo="Sensor da Qualidade do Sinal",
            funcao=funcao,
            unidade=unidade,
        ) 
"""*Criação dos Sensores do Módulo Comunicação*"""

class SensorIntegridadeEstrutural(Sensores):
    
    def __init__ (self, nome: str, funcao: str, unidade: str,integridadeEstrutural: float = 100.0):       
       super().__init__(
            nome=nome,
            tipo="Sensor da Integridade Estrutural",
            funcao=funcao,
            unidade=unidade,
        )  
       self.integridadeEstrutural = integridadeEstrutural
       
"""*Criação dos Sensores do Módulo Habitat*"""

class SensorTemperaturaExterna(Sensores):

    def __init__ (self, nome: str, funcao: str, unidade: str):
       super().__init__(
            nome=nome,
            tipo="Sensor da Temperatura Externa",
            funcao=funcao,
            unidade=unidade,
        ) 
class SensorRadicao(Sensores):

    def __init__ (self, nome: str, funcao: str, unidade: str):
       super().__init__(
            nome=nome,
            tipo="Sensor da Radiação",
            funcao=funcao,
            unidade=unidade,
        )  

"""*Criação dos Sensores do Módulo Laboratório *"""

class SensorHelio3(Sensores):

    def __init__ (self, nome: str, funcao: str, unidade: str):
       super().__init__(
            nome=nome,
            tipo="Sensor do Hélio 3",
            funcao=funcao,
            unidade=unidade,
        ) 

"""*Crição dos Sensores do Módulo Armazenamento*"""
