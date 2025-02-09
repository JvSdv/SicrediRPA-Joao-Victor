from playwright.sync_api import Playwright
import os

class calculoExatoWebScraper:
    def __init__(
        self,
        valor_a_ser_atualizado: float,
        data_inicial: str,
        data_final: str,
        indice: str
    ):

        # --------------------------------------------------------------------------
        # Parâmetros básicos para o cálculo
        # --------------------------------------------------------------------------
        self.valor_a_ser_atualizado = valor_a_ser_atualizado
        self.data_inicial = data_inicial  # Formato "dd/mm/aaaa"
        self.data_final = data_final      # Formato "dd/mm/aaaa"
        self.indice = indice              # Ex: "igpm", "ipca", etc.

        # --------------------------------------------------------------------------
        # URLs e XPaths principais (ajuste conforme seu cenário)
        # --------------------------------------------------------------------------
        self.url = "https://calculoexato.com.br/menu.aspx"

        self.xpath_calculos_financeiros = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/ul/li[1]/strong/a"""
        self.xpath_atualizacao_valor_por_indice_financeiro = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/form/div[3]/div[2]/span[1]/div/ul/li[3]/strong/a"""

        self.full_xpath_valor_a_ser_atualizado = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div/span[3]/div/input"""

        self.full_xpath_dia_inicial = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div/span[4]/div/select[3]"""
        self.full_xpath_mes_inicial = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div/span[4]/div/select[2]"""
        self.full_xpath_ano_inicial = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div/span[4]/div/select[1]"""

        self.full_xpath_dia_final = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div/span[5]/div/select[3]"""
        self.full_xpath_mes_final = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div/span[5]/div/select[2]"""
        self.full_xpath_ano_final = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div/span[5]/div/select[1]"""

        self.full_xpath_indice = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div/span[6]/div/select"""
        self.full_xpath_botao_continuar = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/div[1]/input"""

        # Estes XPaths são onde coletaremos apenas os textos crus do resultado:
        self.full_xpath_valor_atualizado = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div[2]/div[1]/p[1]/b"""
        self.full_xpath_percentual_final__fator_multiplicacao__meses_percentuais = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div[2]/div[1]/p[2]"""

        # --------------------------------------------------------------------------
        # Estrutura para armazenar o resultado "cru" (sem parse numérico)
        # --------------------------------------------------------------------------
        self.result = {
            "valorInformado": self.valor_a_ser_atualizado,
            "dataInicial": self.data_inicial,
            "dataFinal": self.data_final,
            "indice": self.indice,
            "retornoDaConsulta": False,
            # Os campos abaixo serão preenchidos após a navegação
            "raw_valor_atualizado": None,
            "raw_percentual_info": None
        }

        # Variáveis internas para Playwright
        self.context = None
        self.page = None

    def start_browser(self, playwright: Playwright, headless=False):
        """
        Inicia um contexto persistente do Chromium com a extensão de adblock,
        localizada na subpasta "adblocker_extension".
        """
        path_to_extension = os.path.join(os.getcwd(), "util", "adblocker_extension")

        self.context = playwright.chromium.launch_persistent_context(
            user_data_dir="",
            channel="chromium",
            headless=headless,
            slow_mo=1000,
            args=[
                f"--disable-extensions-except={path_to_extension}",
                f"--load-extension={path_to_extension}"
            ],
        )

        if not self.context.pages:
            self.page = self.context.new_page()
        else:
            self.page = self.context.pages[0]

    def close_browser(self):
        """Encerra o contexto e, consequentemente, o browser."""
        if self.context:
            self.context.close()

    def go_to_site(self):
        """Navega até a página inicial."""
        self.page.goto(self.url, timeout=20000)
        self.page.wait_for_timeout(3000)
        self.page.reload()

    def click_calculos_financeiros(self):
        """Clica na opção 'Cálculos financeiros'."""
        self.page.wait_for_selector(self.xpath_calculos_financeiros, timeout=5000)
        self.page.click(self.xpath_calculos_financeiros, timeout=5000)
        self.page.wait_for_load_state("networkidle", timeout=10000)

    def click_atualizacao_valor_por_indice_financeiro(self):
        """Clica na opção 'Atualização de valor por índice financeiro'."""
        self.page.wait_for_selector(self.xpath_atualizacao_valor_por_indice_financeiro, timeout=5000)
        self.page.click(self.xpath_atualizacao_valor_por_indice_financeiro)
        self.page.wait_for_load_state("networkidle", timeout=10000)

    def fill_valor_a_ser_atualizado(self):
        """
        Preenche o valor a ser atualizado no formato brasileiro com vírgula
        (ex.: 50000.00 => "50.000,00").
        """
        valor_str = f"{self.valor_a_ser_atualizado:,.2f}"  # "50,000.00" no Python
        valor_str = valor_str.replace(",", "X").replace(".", ",").replace("X", ".")
        self.page.wait_for_selector(self.full_xpath_valor_a_ser_atualizado, timeout=6000)
        self.page.fill(self.full_xpath_valor_a_ser_atualizado, valor_str)

    def select_date_inicial(self):
        """Seleciona o dia, mês e ano da data inicial."""
        day, month, year = self.data_inicial.split("/")
        self.page.wait_for_selector(self.full_xpath_dia_inicial, timeout=6000)
        self.page.select_option(self.full_xpath_dia_inicial, day)
        self.page.select_option(self.full_xpath_mes_inicial, month)
        self.page.select_option(self.full_xpath_ano_inicial, year)

    def select_date_final(self):
        """Seleciona o dia, mês e ano da data final."""
        day, month, year = self.data_final.split("/")
        self.page.wait_for_selector(self.full_xpath_dia_final, timeout=6000)
        self.page.select_option(self.full_xpath_dia_final, day)
        self.page.select_option(self.full_xpath_mes_final, month)
        self.page.select_option(self.full_xpath_ano_final, year)

    def select_indice(self):
        """Seleciona o índice desejado (ex: 'igpm')."""
        self.page.wait_for_selector(self.full_xpath_indice, timeout=6000)
        self.page.select_option(self.full_xpath_indice, self.indice)

    def click_continuar(self):
        """Clica no botão 'Continuar' para efetuar o cálculo."""
        self.page.wait_for_selector(self.full_xpath_botao_continuar, timeout=6000)
        self.page.click(self.full_xpath_botao_continuar)
        self.page.wait_for_load_state("networkidle", timeout=10000)

    def parse_resultado_calculo(self):
        """
        Faz apenas a leitura (coleta) dos textos crus do site,
        sem converter para float. Armazenamos no self.result.
        """
        try:
            # Valor atualizado em texto
            self.page.wait_for_selector(self.full_xpath_valor_atualizado, timeout=8000)
            raw_valor_atualizado_str = self.page.inner_text(self.full_xpath_valor_atualizado)

            # Texto que contém o percentual final, fator de multiplicação etc.
            self.page.wait_for_selector(
                self.full_xpath_percentual_final__fator_multiplicacao__meses_percentuais,
                timeout=8000
            )
            raw_percentual_info_str = self.page.inner_text(
                self.full_xpath_percentual_final__fator_multiplicacao__meses_percentuais
            )

            self.result["raw_valor_atualizado"] = raw_valor_atualizado_str
            self.result["raw_percentual_info"] = raw_percentual_info_str
            self.result["retornoDaConsulta"] = True

        except Exception as e:
            print("Erro ao coletar resultado bruto:", e)
            self.result["retornoDaConsulta"] = False

    def run(self):
        """Executa todo o fluxo de forma sequencial até obter os textos crus."""
        self.go_to_site()
        self.click_calculos_financeiros()
        self.click_atualizacao_valor_por_indice_financeiro()
        self.fill_valor_a_ser_atualizado()
        self.select_date_inicial()
        self.select_date_final()
        self.select_indice()
        self.click_continuar()
        self.parse_resultado_calculo()

    def get_result(self) -> dict:
        """Retorna o dicionário com as informações coletadas (brutas)."""
        return self.result

    def print_result(self):
        """Imprime o resultado cru atual do cálculo (antes de qualquer conversão)."""
        print(self.result)