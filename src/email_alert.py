import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAlert:
    def __init__(self, config):
        self.config = config
        self.ativo = config.get("ativo", False)
        self.ultimo_envio = {}  # Evita spam de e-mails
    
    def pode_enviar(self, tipo):
        """Evita enviar múltiplos e-mails do mesmo tipo em menos de 5 minutos"""
        import time
        agora = time.time()
        
        if tipo in self.ultimo_envio:
            tempo_decorrido = agora - self.ultimo_envio[tipo]
            if tempo_decorrido < 300:  # 5 minutos
                return False
        
        self.ultimo_envio[tipo] = agora
        return True
    
    def enviar(self, tipo, valor):
        if not self.ativo:
            return False
        
        # Evita spam de e-mails
        if not self.pode_enviar(tipo):
            return False
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.config["remetente"]
            msg["To"] = self.config["destinatario"]
            msg["Subject"] = f"🚨 ALERTA: {tipo.upper()} em {valor:.2f}%"
            
            corpo = f'''
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #ef4444;">⚠️ Alerta de Recursos do Servidor</h2>
                    <div style="background: #fee; padding: 15px; border-radius: 5px; border-left: 4px solid #ef4444;">
                        <p><strong>Recurso:</strong> {tipo.upper()}</p>
                        <p><strong>Uso Atual:</strong> <span style="color: #dc2626; font-size: 1.2em;">{valor:.2f}%</span></p>
                        <p><strong>Limite Configurado:</strong> 90%</p>
                    </div>
                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 0.9em;">
                        Este é um alerta automático do Monitor de Recursos.<br>
                        Para evitar spam, você receberá no máximo 1 e-mail a cada 5 minutos por tipo de alerta.
                    </p>
                </body>
            </html>
            '''
            
            msg.attach(MIMEText(corpo, "html"))
            
            # Conecta ao servidor SMTP
            print(f"📧 Conectando ao servidor SMTP...")
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            server.set_debuglevel(0) 
            
            print(f"🔐 Iniciando TLS...")
            server.starttls()
            
            print(f"🔑 Fazendo login...")
            server.login(self.config["remetente"], self.config["senha"])
            
            print(f"📤 Enviando e-mail...")
            server.send_message(msg)
            server.quit()
            
            print(f"✅ E-mail enviado com sucesso para {self.config['destinatario']}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ ERRO DE AUTENTICAÇÃO: Verifique seu e-mail e senha de app")
            print(f"   Detalhes: {e}")
            return False
            
        except smtplib.SMTPException as e:
            print(f"❌ ERRO SMTP: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Erro inesperado ao enviar e-mail: {type(e).__name__}")
            print(f"   Detalhes: {e}")
            return False