
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
        return "Nenhum evento crítico registrado." #Esse é o else caso não tenha evento na pilha
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

    def alterar_status(self, nove_status: bool):
        '''Visualizar status'''
        self.status = nove_status   


#-----------------Sistemas-----------------#
class Sistema:
    '''Classe que representa os sistemas, tanto de geração quanto armazenamento'''
    def __init__(self, nome: str, capacidade_max_geracao: int, geracao_atual: int, capacidade_max_armazenamento: int):
        '''
        Args:
            nome: Nome do Sistema.
            capacidade_max: Capacidade maxima de geração do sistema.
            geracao_atual: Geração atual.
            capacidade_max_armazenamento: Capacidade maxima de armazenamento do sistema.
        '''
        self.nome = nome
        self.capacidade_max_geracao = capacidade_max_geracao
        self.geracao_atual = geracao_atual
        self.capacidade_max_armazenamento = capacidade_max_armazenamento
        
class SistemaGeracaoSolar(Sistema):
    '''Painéis Solares.'''
    def __init__(self, nome: str, capacidade_max_geracao: int, geracao_atual: int):
        super().__init__(nome, capacidade_max_geracao, geracao_atual, capacidade_max_armazenamento = 0)

class SistemaGeracaoEolica(Sistema):
    '''Turbinas Eolicas.'''
    def __init__(self, nome: str, capacidade_max_geracao: int, geracao_atual: int):
        super().__init__(nome, capacidade_max_geracao, geracao_atual, capacidade_max_armazenamento = 0)

class SistemaArmazenamentoEnergetico(Sistema):
    '''Sistema de baterias.'''
    def __init__(self, nome: str, capacidade_max_armazenamento: int = 100):
        super().__init__(nome, capacidade_max_geracao=0, geracao_atual=0, capacidade_max_armazenamento=capacidade_max_armazenamento)

#-----------------Sensores-----------------#
class Sensores: 
    '''Classe para representar os sensores da missão.'''
    def __init__(self, nome: str, tipo: str, funcao: str, leitura: str, unidade: str, integridadeEstrutural: float = 100.0):
        '''
        Args:
            nome: Nome do sensor.
            tipo: Categoria do sensor (Sensor de Temperatura, Sensor de Pressão, Sensor de Umidade, Sensor de Radiação, Sensor de Movimento)
            funcao: Descrição da função do sensor.
            leitura: Valor atual da leitura do sensor.
            unidade: Unidade da leitura (°C, hPa, %, mSv/h, m/s²)
        '''
        self.nome = nome
        self.tipo = tipo
        self.funcao = funcao
        self.leitura = leitura
        self.unidade = unidade
        
class SensorIrradiacao(Sensores):
    '''Sensor de Irradiacao.'''
    def __init__(self, nome: str, funcao: str, leitura: str, unidade: str):
        ...        

class SensorVelocidadeVento(Sensores):
    '''Sensor de Velocidade do Vento.'''
    def __init__(self, nome: str, funcao: str, leitura: str, unidade: str):
        ...

class SensorNivelEnergia(Sensores):
    '''Sensor de Nivel de Energia.'''
    def __init__(self, nome: str, funcao: str, leitura: str, unidade: str):
        ...