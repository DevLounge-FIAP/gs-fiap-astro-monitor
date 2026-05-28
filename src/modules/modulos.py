
class Missao_espacial:
    '''
    Parte central da missão. Agrega todos os módulos e sistemas.
    '''
    def __init__(self):
        self.modulos = []
        self.sistemas = []
        self.sensores = []


class Modulo:
    '''
    Representação de um módulo físico da missão
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

    def __repr__(self):
        estado = "Ligado" if self.status else "Desligado"
        return f"Módulo: {self.id_nome} ({self.funcao}) [{estado}] Criticidade: {self.criticidade}"


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
        ...
    

class SistemaGeracaoEolica(Sistema):
    '''Turbinas Eolicas.'''
    def __init__(self, nome: str, capacidade_max_geracao: int, geracao_atual: int):
        ...

class SistemaArmazenamentoEnergetico(Sistema):
    '''Sistema de baterias.'''
    def __init__(self, nome: str, capacidade_max_armazenamento: int):
        ...

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
