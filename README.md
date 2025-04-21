# 🐇 RabbitMQ Tasks Prototype - Sistemas Distribuidos

Protótipo de comunicação cliente-servidor utilizando RabbitMQ em Python, com foco em aplicações acadêmicas e ambientes reais ou virtualizados. O servidor executa três tarefas básicas mediante requisições do cliente:
- 📩 Responde mensagens de texto.
- 📝 Altera um arquivo `.txt`.
- 🧮 Calcula uma função matemática simples.


## ⚙️ Tecnologias Utilizadas

- Python 3.10+
- RabbitMQ
- Biblioteca [`pika`](https://pika.readthedocs.io/en/stable/)

## 🧠 Como Funciona

1. O cliente envia uma mensagem via RabbitMQ para uma fila RPC.
2. O servidor consome essa mensagem, executa a tarefa solicitada e responde na fila de retorno.
3. O cliente aguarda e imprime a resposta.