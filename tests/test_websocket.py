import socketio
import time
import json

def test_websocket():
    print("🔌 Testando conexão WebSocket...")
    
    # Criar cliente Socket.IO
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print("✅ Conectado ao servidor WebSocket!")
        
        # Testar envio de mensagem
        test_message = {
            'message': 'Teste de mensagem',
            'chat_type': 'private',
            'recipient_id': 1
        }
        
        print(f"📤 Enviando mensagem de teste: {test_message}")
        sio.emit('send_message', test_message)
        
        # Aguardar um pouco e desconectar
        time.sleep(2)
        sio.disconnect()
    
    @sio.event
    def disconnect():
        print("🔌 Desconectado do servidor WebSocket")
    
    @sio.on('private_message')
    def on_private_message(data):
        print(f"📨 Mensagem privada recebida: {data}")
    
    @sio.on('error')
    def on_error(data):
        print(f"❌ Erro recebido: {data}")
    
    @sio.on('notification')
    def on_notification(data):
        print(f"🔔 Notificação recebida: {data}")
    
    try:
        # Conectar ao servidor
        sio.connect('http://localhost:5001')
        
        # Aguardar um pouco para receber respostas
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
    
    finally:
        if sio.connected:
            sio.disconnect()

if __name__ == "__main__":
    test_websocket() 