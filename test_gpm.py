import os
from download_gpm import Chrome
from get_date_run import writeDate
from auxiliar import path_temp, path_downloads
import shutil

def test_gpm_single():
    print("=== INICIANDO TESTE UNITÁRIO GPM ===")
    
    # Configura uma data de teste se necessário
    # writeDate("2024-03-01T00:00:00") 
    
    chrome = Chrome()
    
    # 1. Limpeza inicial
    print("- Limpando ambiente de teste...")
    chrome.limpar_pasta_temp()
    chrome.limpar_downloads_inicial()
    
    # 2. Executa apenas para BA como teste
    try:
        print("- Testando Operação BA...")
        chrome.baixar_consulta_turno("BA")
        
        # 3. Verifica se o arquivo apareceu na pasta temp
        esperado = os.path.join(path_temp, "consulta turno BA.csv")
        if os.path.exists(esperado):
            tamanho = os.path.getsize(esperado)
            print(f"✅ SUCESSO: Arquivo gerado em {esperado} ({tamanho} bytes)")
            
            # Lê as primeiras linhas para ver se tem datas
            with open(esperado, 'r', encoding='utf-8-sig') as f:
                linhas = [f.readline() for _ in range(3)]
                print("- Conteúdo do arquivo gerado:")
                for l in linhas:
                    print(f"  > {l.strip()}")
        else:
            print("❌ FALHA: Arquivo não foi encontrado na pasta temp.")
            
    except Exception as e:
        print(f"💥 ERRO DURANTE O TESTE: {e}")
    finally:
        print("=== FIM DO TESTE UNITÁRIO ===")

if __name__ == "__main__":
    test_gpm_single()
