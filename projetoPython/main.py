import socketio
import eventlet
import json
from playwright.sync_api import sync_playwright

from src.calculoExatoWebScraper import calculoExatoWebScraper
from src.conversorDados import conversorDados

# Cria instância do servidor Socket.IO (modo padrão, usando eventlet)
sio = socketio.Server(cors_allowed_origins='*', async_mode='eventlet')
app = socketio.WSGIApp(sio)

# Evento de conexão
@sio.event
def connect(sid, environ):
    print(f"[PY] Cliente conectado: {sid}")

# Evento de desconexão
@sio.event
def disconnect(sid):
    print(f"[PY] Cliente desconectado: {sid}")

# Evento customizado: "calculo_financeiro"
# Espera receber JSON com:
# {
#   "valor_a_ser_atualizado": 50000.0,
#   "data_inicial": "02/04/2021",
#   "data_final": "15/10/2024",
#   "indice": "igpm"
# }
@sio.on('calculo_financeiro')
def handle_calculo_financeiro(sid, data):
    try:
        with sync_playwright() as p:
            # data chega como dicionário (se enviado corretamente em JSON)
            # Exemplo de data: {"valor_a_ser_atualizado": 50000.0, ...}

            # Passo 1: executar o scraping
            valor = float(data.get('valor_a_ser_atualizado', 0.0))
            data_inicial = data.get('data_inicial', '01/01/2000')
            data_final = data.get('data_final', '01/01/2000')
            indice = data.get('indice', 'igpm')

            # printar
            print(f"Recebido: {valor}, {data_inicial}, {data_final}, {indice}")

            scraper = calculoExatoWebScraper(
                valor_a_ser_atualizado=valor,
                data_inicial=data_inicial,
                data_final=data_final,
                indice=indice
            )

            # inicia browser (headless=True se quiser sem interface)
            scraper.start_browser(p, headless=False)
            scraper.run()
            raw_result = scraper.get_result()
            scraper.close_browser()

            # Passo 2: fazer a conversão
            conv = conversorDados(raw_result)
            conv.run()
            final_result = conv.get_result()

            # Converte final_result para JSON string
            resposta_json = json.dumps(final_result, ensure_ascii=False)

            # Emite um evento de resposta. Você pode usar o mesmo nome com sufixo "_response"
            # ou enviar para o mesmo sid. Abaixo, exemplo usando “calculo_financeiro_response”.
            sio.emit('calculo_financeiro_response', resposta_json, to=sid)

    except Exception as e:
        print(f"Erro no processamento: {e}")
        sio.emit('calculo_financeiro_response', json.dumps({"erro": "Erro no processamento no serviço python: " +str(e)}), to=sid)

if __name__ == "__main__":
    print("[PY] Servidor socket.io iniciado na porta 5000...")
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)