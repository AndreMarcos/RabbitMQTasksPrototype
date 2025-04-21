"""Servidor RPC para responder comandos via RabbitMQ."""

import os
import json
import requests
import pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")
BOT_URL = os.getenv("BOT_SERVER_URL")


def processar_eco(mensagem):
    """ Processa o comando 'eco' e retorna a mensagem recebida. """
    prompt = mensagem.get('mensagem', '')
    try:
        response = requests.post(
            BOT_URL,
            json={"model": "phi3", "prompt": prompt},
            timeout=10
        )
        resposta = ''
        for linha in response.iter_lines():
            if linha:
                parte = json.loads(linha.decode("utf-8"))
                resposta += parte.get("response", "")
                if parte.get("done", False):
                    break
        return resposta
    except requests.RequestException as e:
        return f"Erro ao acessar o Assistente: {str(e)}"

def processar_arquivo(mensagem):
    """ Processa o comando 'alterar_arquivo' e escreve no arquivo. """
    try:
        with open('arquivo.txt', 'a', encoding='utf-8') as f:
            f.write(mensagem.get('conteudo', '') + '\n')
        return "Arquivo alterado com sucesso."
    except IOError as e:
        return f"Erro ao escrever no arquivo: {str(e)}"

def processar_calculo(mensagem):
    """ Processa o comando 'calcular' e retorna o resultado da função f(x). """
    try:
        x = int(mensagem.get('valor', 0))
        resultado = x**2 + 2 * x + 1
        return f"Resultado da função f(x): {resultado}"
    except (ValueError, TypeError):
        return "Erro: valor inválido para cálculo."

def processar_mensagem(mensagem):
    """
    Processa a mensagem recebida via RabbitMQ e retorna a resposta adequada.

    Args:
        mensagem (dict): Dicionário contendo o comando e os parâmetros.

    Returns:
        str: Resposta gerada.
    """
    comando = mensagem.get('comando')

    handlers = {
        'eco': processar_eco,
        'alterar_arquivo': processar_arquivo,
        'calcular': processar_calculo,
    }

    handler = handlers.get(comando)
    if handler:
        return handler(mensagem)
    return "Comando não reconhecido."


def on_request(ch, method, props, body):
    """
    Função chamada ao receber uma requisição RPC.

    Args:
        ch: Canal de comunicação.
        method: Método usado para entrega.
        props: Propriedades da mensagem.
        body: Corpo da mensagem (bytes).
    """
    dados = json.loads(body)
    resposta = processar_mensagem(dados)

    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=str(resposta),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    """Inicializa o servidor e começa a escutar a fila RPC."""
    credenciais = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parametros = pika.ConnectionParameters(RABBITMQ_HOST, credentials=credenciais)
    conexao = pika.BlockingConnection(parametros)
    canal = conexao.channel()

    canal.queue_declare(queue=RABBITMQ_QUEUE)
    canal.basic_qos(prefetch_count=1)
    canal.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=on_request)

    print("[Servidor] Aguardando requisições...")
    canal.start_consuming()


if __name__ == "__main__":
    main()
