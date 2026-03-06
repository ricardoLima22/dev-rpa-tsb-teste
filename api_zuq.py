import os
import requests
import json
from get_date_run import getInitialDate, getFinalDate 
from auxiliar import *

def relatorio_zuq():
    # Definindo a URL base
    base_url = "https://app.zuq.com.br"

    # Endpoint para extrair o relatório de notificações
    data_endpoint = "/api/notification/list"

    try:
        print(f'{l}- Iniciando integração com API ZUQ...') # LINHA NOVA ADICIONADA

        # Obtendo as datas de início e fim no formato yyyy-mm-dd
        start_date = getInitialDate().split("T")[0]
        end_date = getFinalDate().split("T")[0]

        if start_date and end_date:
            # Configurando o cabeçalho com o token de autenticação
            headers = {
                "Authorization": f"{token_zuq}"
            }
            page = 1
            dados_agregados = []

            while True:
                # Configurando os parâmetros da consulta para a página atual
                params = {
                    "start": start_date,
                    "end": end_date,
                    "page": page,
                    "size": 500,
                    "property": "ODOMETER"
                }

                # Fazendo a requisição GET para extrair os dados
                data_response = requests.get(base_url + data_endpoint, headers=headers, params=params)
                print(f"Data response: {data_response}")
                # Verificando se a requisição foi bem-sucedida
                data_response.raise_for_status()
                data = data_response.json()

                # Verifica se a lista retornada está vazia; se sim, sai do loop
                if not data:
                    break

                # Adiciona os dados retornados à lista agregada
                dados_agregados.extend(data)

                # Incrementa para a próxima página
                page += 1

            # Salvando o resultado em um arquivo JSON
            with open(notifications_file, "w") as json_file:
                json.dump(dados_agregados, json_file, indent=4)
            print(f"- Relatório salvo com sucesso em: {notifications_file}\n")
        else:
            print("# As datas não foram obtidas corretamente. Verifique o arquivo JSON.")

    except requests.exceptions.RequestException as e:
        print(f"# Erro na requisição: {e}\n")
        # Cria arquivo vazio para não travar o restante do robô        
        with open(notifications_file, "w") as json_file:
            json.dump([], json_file)
            
    except json.JSONDecodeError:
        print("# Erro ao decodificar a resposta JSON.")
        # Cria arquivo vazio para não travar        
        with open(notifications_file, "w") as json_file:
            json.dump([], json_file)

    except Exception as e:
        print(f"# Ocorreu um erro genérico: {e}")
        # Cria arquivo vazio para não travar        
        with open(notifications_file, "w") as json_file:
            json.dump([], json_file)
        
if __name__ == "__main__":
    relatorio_zuq()