from collections import deque

'''Aqui vou usar uma fila dupla que é propria do Python e não se enquadra como biblioteca avançada.
    Vou usar ela pois garante adição(.append) e remoção(.pop) O(1) em ambas as extremidades.
    Onde uma lista normal é O(1) para .append no final e O(n) para .pop no inicio.

Aqui uma comparação rapida.

Comparação:                 Lista vs. Deque
Operação	        Lista (list)	   Deque (collections.deque)
Append no final	        O(1)	                    O(1)
Append no início	    O(n)                      	O(1)
Pop no final	        O(1)                        O(1)
Pop no início	        O(n)	                    O(1)
Acesso por índice	    O(1)	        O(1) nas extremidades, O(n) no meio
'''
# Parte do Aelton(Eu) tambem, aqui é para os alertas gerados respeitarem uma lógica e armazenamento.
class CentralDeAlertas:
    '''
    Gerenciador dos alertas da missão
    Utiliza uma Fila em deque, processa por ondem de chegada (FIFO).
    '''
    def __init__(self):

        self.fila_de_alertas = deque()

    def enfileirar_alerta(self, severidade: str, mensagem: str, recomendacao: str):
        '''
        Faz a entrada na Fila.
        Tem que chamar esse metodo SEMPRE que um IF achar problema.
        '''
        alerta = {
            'severidade': severidade.upper(), #Exemplo: 'NORMAL', 'ALERTA', 'CRITICO'. #Definir isso nas regras
            'mensagem': mensagem, #Definir isso nas regras
            'recomendacao': recomendacao #Definir isso nas regras
        }

        self.fila_de_alertas.append(alerta)
        print(f"[NOVO ALERTA ENFILEIRADO] Nível: {severidade.upper()}, Mensagem:{mensagem}")

    def processar_proximo_alerta(self):
        '''
        Faz a saida na Fila
        '''
        if self.fila_de_alertas:
            alerta_tratado = self.fila_de_alertas.popleft() #popleft pois é deque.
            return alerta_tratado
        
        else:
            return None #Retorna None se não tem alertar pendentes.
        
    def obter_quantidade_alertas_pendentes(self) -> int:
        '''
        Método auxiliar para o sistema orquestrador para saber tem tem alerta pendente.
        '''
        return len(self.fila_de_alertas)