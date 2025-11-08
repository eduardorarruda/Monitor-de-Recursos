import psutil
import time
import json
import os
import sys
import schedule
from datetime import datetime


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_manager import LogManager
from email_alert import EmailAlert

class MonitorRecursos:
    def __init__(self, config_path="config/config.json"):
        self.carregar_config(config_path)
        self.log_manager = LogManager()
        self.email_alert = EmailAlert(self.config.get("email", {}))
        self.historico = []
    
    def carregar_config(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.limites = self.config["limites"]
        self.intervalo = self.config["intervalo_verificacao"]
    
    def coletar_dados(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": psutil.cpu_percent(interval=1),
            "memoria": psutil.virtual_memory().percent,
            "disco": psutil.disk_usage('/').percent
        }
    
    def verificar_alertas(self, dados):
        alertas = []
        
        for recurso in ["cpu", "memoria", "disco"]:
            valor = dados[recurso]
            limite = self.limites[recurso]
            
            if valor > limite:
                # Registra no log
                msg = self.log_manager.registrar(recurso, valor)
                print(f"\n🚨 {msg}")
                
                # Envia e-mail
                if self.email_alert.ativo:
                    self.email_alert.enviar(recurso, valor)
                
                alertas.append({"tipo": recurso, "valor": valor})
        
        return alertas
    
    def exibir_status(self, dados):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] CPU: {dados['cpu']:.1f}% | "
              f"MEM: {dados['memoria']:.1f}% | "
              f"DISCO: {dados['disco']:.1f}%", end="\r")
    
    def executar(self):
        print("=" * 50)
        print("=== Monitor de Recursos Avançado ===")
        print("=" * 50)
        print(f"\n⚙️  Limites Configurados:")
        print(f"   • CPU: {self.limites['cpu']}%")
        print(f"   • Memória: {self.limites['memoria']}%")
        print(f"   • Disco: {self.limites['disco']}%")
        
        # Status do e-mail
        if self.email_alert.ativo:
            print(f"\n📧 E-mail: ✅ ATIVO")
            print(f"   • Remetente: {self.config['email']['remetente']}")
            print(f"   • Destinatário: {self.config['email']['destinatario']}")
        else:
            print(f"\n📧 E-mail: ❌ DESATIVADO")
            print(f"   Para ativar, mude 'ativo' para true no config.json")
        
        print("\n" + "=" * 50)
        print("Monitoramento iniciado! Pressione Ctrl+C para parar\n")
        
        # Agenda limpeza de logs
        if self.config["limpeza_logs"]["ativo"]:
            dias = self.config["limpeza_logs"]["dias_manter"]
            schedule.every().day.at("03:00").do(
                lambda: self.log_manager.limpar_logs_antigos(dias)
            )
        
        try:
            while True:
                schedule.run_pending()
                
                dados = self.coletar_dados()
                self.historico.append(dados)
                
                # Mantém apenas últimas 100 leituras
                if len(self.historico) > 100:
                    self.historico.pop(0)
                
                self.exibir_status(dados)
                self.verificar_alertas(dados)
                
                time.sleep(self.intervalo)
        
        except KeyboardInterrupt:
            print("\n\n=== Monitor Encerrado pelo Usuário ===")

if __name__ == "__main__":
    monitor = MonitorRecursos()
    monitor.executar()