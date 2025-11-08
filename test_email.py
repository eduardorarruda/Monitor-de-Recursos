import json
import sys
import os

# Adiciona src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from email_alert import EmailAlert

print("=" * 60)
print("🧪 TESTE DE ENVIO DE E-MAIL")
print("=" * 60)

# Carrega configurações
try:
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    print("❌ Arquivo config/config.json não encontrado!")
    exit(1)

email_config = config.get("email", {})

# Exibe configurações (sem mostrar senha completa)
print(f"\n📋 Configurações atuais:")
print(f"   • Ativo: {email_config.get('ativo', False)}")
print(f"   • Remetente: {email_config.get('remetente', 'não configurado')}")
print(f"   • Destinatário: {email_config.get('destinatario', 'não configurado')}")
print(f"   • Servidor: {email_config.get('smtp_server', 'não configurado')}")
print(f"   • Porta: {email_config.get('smtp_port', 'não configurado')}")

senha = email_config.get('senha', '')
if senha:
    print(f"   • Senha: {senha[:4]}{'*' * (len(senha) - 4)}")
else:
    print(f"   • Senha: não configurada")

# Verifica se está ativo
if not email_config.get("ativo", False):
    print("\n⚠️  ALERTA: E-mail está desativado no config.json")
    print("   Para ativar, mude 'ativo' para true")
    
    resposta = input("\n❓ Deseja testar mesmo assim? (s/n): ")
    if resposta.lower() != 's':
        print("❌ Teste cancelado")
        exit(0)
    
    # Força ativação temporária para teste
    email_config["ativo"] = True

# Valida configurações obrigatórias
campos_obrigatorios = ["remetente", "senha", "destinatario", "smtp_server", "smtp_port"]
faltando = [campo for campo in campos_obrigatorios if not email_config.get(campo)]

if faltando:
    print(f"\n❌ ERRO: Campos obrigatórios faltando no config.json:")
    for campo in faltando:
        print(f"   • {campo}")
    exit(1)

# Cria objeto de e-mail e tenta enviar
print("\n" + "=" * 60)
print("📤 Enviando e-mail de teste...")
print("=" * 60 + "\n")

email_alert = EmailAlert(email_config)
sucesso = email_alert.enviar("teste", 95.5)

print("\n" + "=" * 60)
if sucesso:
    print("✅ TESTE BEM-SUCEDIDO!")
    print(f"   Verifique a caixa de entrada de: {email_config['destinatario']}")
    print("   Não esqueça de verificar a pasta de SPAM também!")
else:
    print("❌ TESTE FALHOU!")
    print("\n🔍 Possíveis causas:")
    print("   1. Senha de app incorreta ou expirada")
    print("   2. Verificação em 2 etapas não ativada no Gmail")
    print("   3. E-mail/senha incorretos")
    print("   4. Firewall bloqueando conexão SMTP")
    print("\n💡 Como corrigir:")
    print("   1. Acesse: https://myaccount.google.com/apppasswords")
    print("   2. Gere uma nova senha de app")
    print("   3. Atualize a senha no config.json")
    print("   4. Execute este teste novamente")

print("=" * 60)