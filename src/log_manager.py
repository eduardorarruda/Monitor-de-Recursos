import os
from datetime import datetime, timedelta

class LogManager:
    def __init__(self, pasta_logs="logs"):
        self.pasta_logs = pasta_logs
        os.makedirs(pasta_logs, exist_ok=True)
    
    def registrar(self, tipo, valor):
        arquivo = os.path.join(self.pasta_logs, f"alerta_{tipo}.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mensagem = f"[{timestamp}] ALERTA: {tipo.upper()} em {valor:.2f}%\n"
        
        with open(arquivo, "a", encoding="utf-8") as log:
            log.write(mensagem)
        
        return mensagem.strip()
    
    def limpar_logs_antigos(self, dias=7):
        limite = datetime.now() - timedelta(days=dias)
        
        for arquivo in os.listdir(self.pasta_logs):
            caminho = os.path.join(self.pasta_logs, arquivo)
            
            if os.path.isfile(caminho) and arquivo.endswith(".log"):
                mod_time = datetime.fromtimestamp(os.path.getmtime(caminho))
                
                if mod_time < limite:
                    os.remove(caminho)
                    print(f"Log antigo removido: {arquivo}")
    
    def obter_alertas_recentes(self, horas=24):
        alertas = []
        limite = datetime.now() - timedelta(hours=horas)
        
        for arquivo in os.listdir(self.pasta_logs):
            if arquivo.endswith(".log"):
                caminho = os.path.join(self.pasta_logs, arquivo)
                
                try:
                    with open(caminho, "r", encoding="utf-8") as log:
                        for linha in log:
                            try:
                                data_str = linha.split("]")[0][1:]
                                data = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
                                
                                if data >= limite:
                                    alertas.append({
                                        "timestamp": data_str,
                                        "mensagem": linha.strip()
                                    })
                            except:
                                continue
                except:
                    continue
        
        return sorted(alertas, key=lambda x: x["timestamp"], reverse=True)