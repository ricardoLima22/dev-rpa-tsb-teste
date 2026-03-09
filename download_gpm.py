from datetime import datetime, timedelta
import os
import time
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from get_date_run import getInitialDate
import shutil
from auxiliar import *

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # TensorFlow logs: erros apenas

class Chrome:
    def __init__(self):
        """Construtor que configura todas as opções do Chrome."""
        self.options = webdriver.ChromeOptions()

        if 'GITHUB_ACTIONS' in os.environ:
            self.options.add_argument('--headless=new')
        
        # self.options.add_argument('--headless') # janela oculta
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--force-device-scale-factor=0.67') # Zoom
        
        # Desabilita o carregamento de imagens para acelerar
        self.options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
        
        # Define o diretório de download para a pasta temp do projeto
        self.options.add_experimental_option('prefs', {
            "download.default_directory": os.path.abspath(path_downloads),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        
        # Oculta logs desnecessários
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.navegador = None
        self.janela_web_atual = None

    def _navegar(self, destino):      
        if not self.navegador:
            self.navegador = webdriver.Chrome(options=self.options)
            
            if 'GITHUB_ACTIONS' in os.environ:
                self.navegador.execute_cdp_cmd("Page.setDownloadBehavior", {
                    "behavior": "allow",
                    "downloadPath": os.path.abspath(path_downloads)
                })
            
            self.janela_web_atual = self.navegador.current_window_handle
            
        print(f"- Acessando página web: {destino}")
        self.navegador.get(destino)  

    def _fechar_chrome(self):
        if self.navegador:
            self.navegador.quit()
            self.navegador = None

    def _send_Keys(self, X_PATH, key):
        # Espera o campo estar visível e pronto para receber texto
        elemento = WebDriverWait(self.navegador, 360).until(EC.visibility_of_element_located((By.XPATH, X_PATH)))
        elemento.clear() # LIMPA O CAMPO ANTES DE DIGITAR
        elemento.send_keys(key)
        sleep(0.3)

    def _click(self, X_PATH):
        # Espera o botão estar clicável e rola a tela se necessário
        button = WebDriverWait(self.navegador, 360).until(EC.element_to_be_clickable((By.XPATH, X_PATH)))
        self.navegador.execute_script("arguments[0].scrollIntoView(true);", button)
        sleep(0.5)
        button.click() 

    def _logar_gpm(self, login, senha):
        '''Faz o login no GPM usando os localizadores específicos.'''
        try:
            # 1. Preenche o campo de login por ID
            WebDriverWait(self.navegador, 60).until(EC.visibility_of_element_located((By.ID, "idLogin")))
            self.navegador.find_element(by=By.ID, value="idLogin").send_keys(login)
            sleep(0.3)

            # 2. Preenche o campo de senha por ID
            WebDriverWait(self.navegador, 60).until(EC.visibility_of_element_located((By.ID, "idSenha")))
            self.navegador.find_element(by=By.ID, value="idSenha").send_keys(senha)
            sleep(0.3)

            # 3. Clica no botão de entrar por XPATH
            xpath_entrar = '//input[contains(@value, "ntrar")]'
            WebDriverWait(self.navegador, 60).until(EC.element_to_be_clickable((By.XPATH, xpath_entrar)))
            self.navegador.find_element(by=By.XPATH, value=xpath_entrar).click()
            
            print('- GPM logado com sucesso')
            sleep(5)
            
        except Exception as e:
            print(f'# Erro ao fazer login no GPM: {e}')
            
    def descompactar_e_renomear(self, path_downloads, operacao, tipo_relatorio): #######
        if not os.path.exists(path_temp):
            os.makedirs(path_temp)
        
        files = os.listdir(path_downloads)
        for file in files:
            if file.endswith(".zip") and "consulta" in file.lower():  # evita zip genéricos como o RevoUninstaller
                zip_path = os.path.join(path_downloads, file)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(path_downloads)
                    extracted_files = zip_ref.namelist()
                    print(f"- Arquivo {zip_path} descompactado")

                    for extracted_file in extracted_files:
                        if not extracted_file.endswith(".csv"):
                            continue  # ignora arquivos que não são CSV

                        original_file_path = os.path.join(path_downloads, extracted_file)
                        new_file_name = f"{tipo_relatorio} {operacao}.csv"
                        new_file_path = os.path.join(path_temp, new_file_name)

                        # Se já existir o destino, remove
                        if os.path.exists(new_file_path):
                            os.remove(new_file_path)

                        shutil.move(original_file_path, new_file_path)
                        print(f"- Arquivo renomeado e movido para {new_file_path}")

    def limpar_arquivos_zip(self, diretorio):
        arquivos = os.listdir(diretorio)
        for arquivo in arquivos:
            if arquivo.endswith(".zip"):
                caminho_arquivo = os.path.join(diretorio, arquivo)
                os.remove(caminho_arquivo)
                print(f"- Arquivo {arquivo} removido com sucesso!")

    def getDate(self):
        data_objeto = datetime.strptime(getInitialDate(), "%Y-%m-%dT%H:%M:%S")
        return data_objeto.strftime("%d/%m/%Y")

    def baixar_consulta_turno(self, operacao):

        print(f'{l}- Iniciando download do consulta turno para operação {operacao}')
        login_url = f'https://sirtec{operacao.lower()}.gpm.srv.br/index.php'
        consulta_url = f'https://sirtec{operacao.lower()}.gpm.srv.br/gpm/geral/consulta_turno.php'

        self._navegar(login_url)
        self._logar_gpm(login_gpm, senha_gpm)
        self._navegar(consulta_url)
        
        # INJEÇÃO VIA JAVASCRIPT: Mais confiável para campos com máscara e modo Headless
        data_str = self.getDate()
        print(f"- Injetando datas via JS e disparando eventos: {data_str}")
        
        script_injecao = f"""
            var campos = ['data_inicial', 'data_final'];
            campos.forEach(function(id) {{
                var el = document.getElementById(id);
                el.value = '{data_str}';
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
            }});
        """
        self.navegador.execute_script(script_injecao)
        
        self._click('/html/body/form[5]/div/input')
        
        print("- Aguardando carregamento dos dados na tabela...")
        # Espera dinâmica: Só prossegue se encontrar uma célula com data na tabela
        timeout = 30
        start_time = time.time()
        dados_carregados = False
        
        while time.time() - start_time < timeout:
            try:
                # Procura por qualquer texto que pareça uma data (dd/mm/aaaa) dentro da tabela de resultados
                celulas = self.navegador.find_elements(By.XPATH, '//*[@id="tab_resultados"]//td')
                for celula in celulas:
                    if len(celula.text.strip()) >= 10: # Ex: 01/01/2024
                        dados_carregados = True
                        break
                if dados_carregados:
                    print("- Dados detectados na tabela!")
                    break
            except:
                pass
            sleep(2)
        
        if not dados_carregados:
            print("# AVISO: Tempo limite de espera por dados atingido. Tentando exportar assim mesmo.")
        
        # Scroll para garantir que o site carregue todas as colunas (Lazy Loading)
        self.navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        self.navegador.execute_script("window.scrollTo(0, 0);")
        sleep(2)
        
        self._click('//*[@id="tab_resultados_wrapper"]/div[1]/button[4]')
        print("- Clique no botão de exportação realizado.")
        sleep(15)

        self._fechar_chrome()

        # Tratamento do arquivo após o download (igual na função antiga)
        self.descompactar_e_renomear(path_downloads, operacao, "consulta turno")
        self.limpar_arquivos_zip(path_downloads)
        print(f'- Processo de download do consulta turno finalizado para operação {operacao}')


##### outros ###             
    def limpar_pasta_temp(self):
        if os.path.exists(path_temp):
            for temp_file in os.listdir(path_temp):
                temp_file_path = os.path.join(path_temp, temp_file)
                try:
                    if os.path.isfile(temp_file_path) or os.path.islink(temp_file_path):
                        os.unlink(temp_file_path)
                    elif os.path.isdir(temp_file_path):
                        shutil.rmtree(temp_file_path)
                except Exception as e:
                    print(f"# Falha ao deletar {temp_file_path}. Razão: {e}\n")
