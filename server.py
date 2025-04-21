import os
import pika
import json
import requests
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")
BOT_URL = os.getenv("BOT_SERVER_URL")

def processar_mensagem(mensagem):
    comando = mensagem['comando']

    if comando == 'eco':
        prompt = mensagem['mensagem']
        try:
            response = requests.post(BOT_URL, json={
                    "model": "phi3",
                    "prompt": prompt
                    })
            resposta = ''
            for linha in response.iter_lines():
                if linha:
                    parte = json.loads(linha.decode("utf-8"))
                    resposta += parte.get("response", "")
                    if parte.get("done", False):
                        break
            return resposta
        except Exception as e:
            return f"Erro ao acessar o Assistente: {str(e)}"

    elif comando == 'alterar_arquivo':
        with open('arquivo.txt', 'a') as f:
            f.write(mensagem['conteudo'] + '\n')
        return "Arquivo alterado com sucesso."

    elif comando == 'calcular':
        x = mensagem['valor']
        resultado = x**2 + 2*x + 1
        return f"Resultado da função f(x): {resultado}"

    else:
        return "Comando não reconhecido."

def on_request(ch, method, props, body):
    dados = json.loads(body)
    resposta = processar_mensagem(dados)

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=str(resposta),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)
    

credenciais = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parametros = pika.ConnectionParameters(RABBITMQ_HOST, credentials=credenciais)
conexao = pika.BlockingConnection(parametros)
canal = conexao.channel()

canal.queue_declare(queue=RABBITMQ_QUEUE)
canal.basic_qos(prefetch_count=1)
canal.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=on_request)

print("[Servidor] Aguardando requisições...")
canal.start_consuming()