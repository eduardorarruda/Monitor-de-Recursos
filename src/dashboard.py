from flask import Flask, render_template, jsonify
import json
import sys
import os
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitor import MonitorRecursos

app = Flask(__name__, static_folder="../static", template_folder="../static")
monitor = None

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/status")
def status():
    if monitor and monitor.historico:
        return jsonify(monitor.historico[-1])
    return jsonify({"erro": "Sem dados", "timestamp": None, "cpu": 0, "memoria": 0, "disco": 0})

@app.route("/api/historico")
def historico():
    if monitor:
        return jsonify(monitor.historico)
    return jsonify([])

@app.route("/api/alertas")
def alertas():
    if monitor and monitor.log_manager:
        return jsonify(monitor.log_manager.obter_alertas_recentes())
    return jsonify([])

def executar_monitor():
    """Executa o monitor em thread separada"""
    global monitor
    try:
        monitor = MonitorRecursos()
        monitor.executar()
    except Exception as e:
        print(f"Erro ao executar monitor: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Iniciando Monitor de Recursos com Dashboard")
    print("=" * 50)
    print("\n📊 Dashboard disponível em: http://localhost:5000")
    print("⌨️  Pressione Ctrl+C para encerrar\n")
    
    # Inicia o monitor em uma thread separada
    monitor_thread = threading.Thread(target=executar_monitor, daemon=True)
    monitor_thread.start()
    
    # Aguarda o monitor iniciar
    print("⏳ Aguardando inicialização do monitor...")
    time.sleep(3)
    
    print("✅ Monitor iniciado com sucesso!")
    print("✅ Servidor web iniciado!\n")
    
    # Inicia o servidor Flask
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor encerrado pelo usuário")