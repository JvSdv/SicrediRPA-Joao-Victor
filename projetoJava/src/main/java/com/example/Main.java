package com.example;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;
import org.json.JSONObject;
import org.json.JSONException;

import java.net.URI;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.atomic.AtomicBoolean;

public class Main {

    public static void main(String[] args) {
        // Parâmetros do cálculo
        double valor_a_ser_atualizado = 50000.0;
        String data_inicial = "02/04/2021";
        String data_final = "15/10/2024";
        String indice = "igpm";

        // Timeout máximo em milissegundos (120s = 120000ms)
        long TIMEOUT_MS = 120_000;

        try {
            // Configura a conexão com o servidor Socket.IO em Python (porta 5000)
            URI uri = new URI("http://localhost:5000");
            IO.Options options = new IO.Options();
            options.reconnection = true; // Habilita reconexão automática

            Socket socket = IO.socket(uri, options);

            // Para saber se já recebemos resposta antes do timeout
            AtomicBoolean recebeuResposta = new AtomicBoolean(false);

            // Evento de conexão
            socket.on(Socket.EVENT_CONNECT, new Emitter.Listener() {
                @Override
                public void call(Object... args) {
                    System.out.println("[JAVA] Conectado ao servidor Socket.IO!");

                    try {
                        // Criando JSON com os parâmetros
                        JSONObject payload = new JSONObject();
                        payload.put("valor_a_ser_atualizado", valor_a_ser_atualizado);
                        payload.put("data_inicial", data_inicial);
                        payload.put("data_final", data_final);
                        payload.put("indice", indice);

                        socket.emit("calculo_financeiro", payload);
                        System.out.println("[JAVA] Enviado evento calculo_financeiro ao servidor (JSON): " + payload.toString());
                    } catch (JSONException e) {
                        System.err.println("[JAVA] Erro ao criar JSON: " + e.getMessage());
                    }
                }
            });

            // Evento de resposta do servidor
            socket.on("calculo_financeiro_response", new Emitter.Listener() {
                @Override
                public void call(Object... args) {
                    recebeuResposta.set(true);

                    if (args != null && args.length > 0) {
                        String jsonResposta = args[0].toString();
                        System.out.println("[JAVA] Recebido calculo_financeiro_response: ");
                        System.out.println(jsonResposta);
                    }
                    // Fecha o socket depois de receber a resposta
                    socket.disconnect();
                }
            });

            // Evento de desconexão
            socket.on(Socket.EVENT_DISCONNECT, new Emitter.Listener() {
                @Override
                public void call(Object... args) {
                    System.out.println("[JAVA] Desconectado do servidor Socket.IO!");
                }
            });

            // Conecta de fato
            socket.connect();

            // Inicia um timer de 120s para forçar encerramento se não receber resposta
            Timer timer = new Timer();
            timer.schedule(new TimerTask() {
                @Override
                public void run() {
                    if (!recebeuResposta.get()) {
                        System.out.println("[JAVA] Tempo expirado (120s) sem resposta do servidor!");
                        socket.disconnect();
                    }
                }
            }, TIMEOUT_MS);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
