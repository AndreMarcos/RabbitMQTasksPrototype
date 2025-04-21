import pika
import uuid
import json

class ClienteRPC:
    def __init__(self):
        self.credenciais = pika.PlainCredentials('guest', 'f53jWDpHpn')
        self.parametros = pika.ConnectionParameters('198.27.114.55', credentials=self.credenciais)
        self.connection = pika.BlockingConnection(self.parametros)
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def enviar_requisicao(self, dados):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(dados),
        )
        while self.response is None:
            self.connection.process_data_events()
        return self.response.decode()


def selecionar_comando():
    print("Selecione um comando para enviar ao servidor:")
    print("1. DistribuidosBot")
    print("2. Alterar arquivo")
    print("3. Cálculo")
    comando = input("Digite o número do comando: ")
    return comando



cliente = ClienteRPC()

if __name__ == "__main__":
    while True:
        comando = selecionar_comando()
        if comando == '1':
            mensagem = input("Digite a mensagem para DistribuidosBot: ")
            print(cliente.enviar_requisicao({'comando': 'eco', 'mensagem': mensagem}))
        elif comando == '2':
            conteudo = input("Digite o conteúdo para alterar o arquivo: ")
            print(cliente.enviar_requisicao({'comando': 'alterar_arquivo', 'conteudo': conteudo}))
        elif comando == '3':
            valor = int(input("Digite um número para calcular: "))
            print(cliente.enviar_requisicao({'comando': 'calcular', 'valor': valor}))
        else:
            print("Comando inválido. Tente novamente.")