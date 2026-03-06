import json
from datetime import datetime, timedelta
from auxiliar import *


def writeDate(initial_date, final_date):

    initial_data_object = datetime.strptime(initial_date, "%d/%m/%Y")
    final_data_object = datetime.strptime(final_date, "%d/%m/%Y")

    # Adicionar um dia às datas
    new_initial_date = initial_data_object + timedelta(days=1)
    new_final_date = final_data_object + timedelta(days=1)

    # Definir o final do dia como 23:59:59
    final_do_dia = datetime(new_final_date.year, new_final_date.month, new_final_date.day, 23, 59, 59)

    # Formatar para o formato desejado
    initial_data_format = new_initial_date.strftime("%Y-%m-%dT00:00:00")
    final_data_format = final_do_dia.strftime("%Y-%m-%dT%H:%M:%S")

    try:
        with open(config_json, "r+") as json_file:
            data = json.load(json_file)
            data["initial_date"] = initial_data_format 
            data["final_date"] = final_data_format
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()
            
            print("- Campo 'initial_date e final_date' atualizado com sucesso no arquivo JSON.")
    except FileNotFoundError:
        print("# Arquivo JSON não encontrado para atualizar nova data.")
    except json.JSONDecodeError:
        print("# Erro ao decodificar o JSON para atualizar nova data.")
    except Exception as e:
        print("# Ocorreu um erro para atualizar nova data:", e)

def getInitialDate():
    try:
        with open(config_json, "r") as json_file:
            data = json.load(json_file)
            initial_date = data.get("initial_date")
        if initial_date is not None:
            # print("last_date:", initial_date)
            # Converter a string para objeto datetime
            data_objeto = datetime.strptime(initial_date, "%Y-%m-%dT%H:%M:%S")
            # Formatar para o formato desejado
            data_formatada = data_objeto.strftime("%Y-%m-%dT%H:%M:%S")
            return data_formatada
        else:
            print("# O campo 'initial_date' não foi encontrado no arquivo JSON.")
    except FileNotFoundError:
        print("# Arquivo JSON não encontrado.")
    except json.JSONDecodeError:
        print("# Erro ao decodificar o JSON.")
    except Exception as e:
        print("# Ocorreu um erro:", e)

    return initial_date

def getFinalDate():
    try:
        with open(config_json, "r") as json_file:
            data = json.load(json_file)
            final_date = data.get("final_date")
        if final_date is not None:
            data_objeto = datetime.strptime(final_date, "%Y-%m-%dT%H:%M:%S")
            # Formatar para o formato desejado
            data_formatada = data_objeto.strftime("%Y-%m-%dT%H:%M:%S")
            return data_formatada
        else:
            print("# O campo 'final_date' não foi encontrado no arquivo JSON.")
    except FileNotFoundError:
        print("# Arquivo JSON não encontrado.\n")
    except json.JSONDecodeError:
        print("# Erro ao decodificar o JSON.\n")
    except Exception as e:
        print(f'# Ocorreu um erro: {e} \n')

    return final_date
