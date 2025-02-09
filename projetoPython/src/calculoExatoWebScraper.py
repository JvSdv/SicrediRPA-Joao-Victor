import os
import re
from playwright.sync_api import sync_playwright
from playwright.sync_api import Playwright

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

        self.full_xpath_valor_atualizado = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div[2]/div[1]/p[1]/b"""
        self.full_xpath_percentual_final__fator_multiplicacao__meses_percentuais = """xpath=/html/body/div[4]/table/tbody/tr[2]/td[2]/div[1]/form/div[3]/span[1]/div[2]/div[1]/p[2]"""

        # --------------------------------------------------------------------------
        # Estrutura para armazenar o resultado do cálculo
        # --------------------------------------------------------------------------
        self.result = {
            "valorInformado": self.valor_a_ser_atualizado,
            "dataInicial": self.data_inicial,
            "dataFinal": self.data_final,
            "indice": self.indice,
            "retornoDaConsulta": False,
            "valorAtualizado": None,
            "percentualFinal": None,
            "fatorMultiplicacao": None,
            "mesesPercentuais": None
        }

        # Variáveis internas para Playwright
        self.context = None
        self.page = None

    def start_browser(self, playwright: Playwright, headless=False):
        """
        Inicia um contexto persistente do Chromium com a extensão de adblock,
        localizada na subpasta "adblocker_extension".
        """
        # Caminho até a pasta da extensão (manifest.json etc.)
        path_to_extension = os.path.join(os.getcwd(), "util", "adblocker_extension")

        # Inicia um contexto persistente, pois extensões não funcionam em launch normal
        self.context = playwright.chromium.launch_persistent_context(
            user_data_dir="",           # diretório vazio => não salva nada local
            channel="chromium",         # usar channel Chrome/Chromium para suportar extensões
            headless=headless,          # extensões normalmente não funcionam em headless, mas "chromium" pode permitir
            slow_mo=1000,               # opcional, para ver execução passo-a-passo
            args=[
                f"--disable-extensions-except={path_to_extension}",
                f"--load-extension={path_to_extension}"
            ],
        )

        # Se, ao lançar, não vier nenhuma Page aberta, criamos uma nova
        if not self.context.pages:
            self.page = self.context.new_page()
        else:
            self.page = self.context.pages[0]

    def close_browser(self):
        """Encerra o contexto e, consequentemente, o browser."""
        if self.context:
            self.context.close()

    def parse_br_number(self, br_number_str: str) -> float:
        """
        Converte uma string no formato (ex: "57.005,49") para float (57005.49).
        """
        s = br_number_str.strip()
        s = s.replace('.', '')  # remove pontos de milhar
        s = s.replace(',', '.') # substitui vírgula decimal por ponto
        return float(s)

    def parse_percentual_e_fator(self, text: str):
        """
        A partir do texto no DOM, extrai (percentualFinal, fatorMultiplicacao, textoMeses).
        """
        match_percentual = re.search(r"Em percentual:\s*([\d\.,]+)%", text)
        match_fator = re.search(r"Em fator de multiplicação:\s*([\d\.,]+)", text)

        split_token = "Os valores do índice utilizados neste cálculo foram:"
        partes = text.split(split_token)

        if match_percentual and match_fator and len(partes) > 1:
            percentual_str = match_percentual.group(1)  # ex: "14,0110"
            fator_str = match_fator.group(1)           # ex: "1,140110"
            meses_e_percentuais = partes[1].strip()    # ex: "Abril-2021 = ...%"

            percentual = self.parse_br_number(percentual_str)
            fator = self.parse_br_number(fator_str)
            return percentual, fator, meses_e_percentuais
        else:
            return None, None, None

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
        """Preenche o valor a ser atualizado (usa vírgula como separador decimal)."""
        valor_str = f"{self.valor_a_ser_atualizado:,.2f}"
        # Ajuste: "50.000,00" -> "50.000" => "50,000" -> "50,000" ... 
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
        """Clica no botão 'Continuar' para calcular."""
        self.page.wait_for_selector(self.full_xpath_botao_continuar, timeout=6000)
        self.page.click(self.full_xpath_botao_continuar)
        self.page.wait_for_load_state("networkidle", timeout=10000)

    def parse_resultado_calculo(self):
        """
        Lê os elementos do resultado e preenche self.result com:
          - retornoDaConsulta (bool)
          - valorAtualizado (float)
          - percentualFinal (float)
          - fatorMultiplicacao (float)
          - mesesPercentuais (str)
        """
        try:
            # Valor atualizado
            self.page.wait_for_selector(self.full_xpath_valor_atualizado, timeout=8000)
            valor_atualizado_str = self.page.inner_text(self.full_xpath_valor_atualizado)
            # Exemplo de inner_text: "Valor atualizado: R$57.005,49"
            valor_limpavel = re.sub(r"[^\d,\.]", "", valor_atualizado_str)  # extrair só dígitos, ponto e vírgula
            valor_atualizado_float = self.parse_br_number(valor_limpavel)

            # Percentual final, fator e meses/anos
            self.page.wait_for_selector(
                self.full_xpath_percentual_final__fator_multiplicacao__meses_percentuais,
                timeout=8000
            )
            texto_informacoes_complementares = self.page.inner_text(
                self.full_xpath_percentual_final__fator_multiplicacao__meses_percentuais
            )

            percentual_final, fator_multiplicacao, meses_e_percentuais = self.parse_percentual_e_fator(
                texto_informacoes_complementares
            )

            if (
                valor_atualizado_float is not None and
                percentual_final is not None and
                fator_multiplicacao is not None
            ):
                self.result["retornoDaConsulta"] = True
                self.result["valorAtualizado"] = round(valor_atualizado_float, 2)
                self.result["percentualFinal"] = round(percentual_final, 4)
                self.result["fatorMultiplicacao"] = round(fator_multiplicacao, 6)
                self.result["mesesPercentuais"] = meses_e_percentuais

        except Exception as e:
            # Se deu erro no parsing, deixamos como False
            print("Erro ao parsear resultado:", e)
            self.result["retornoDaConsulta"] = False

    def run(self):
        """Executa todo o fluxo de forma sequencial."""
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
        """Retorna o dicionário com as informações calculadas."""
        return self.result

    def print_result(self):
        """Imprime o resultado atual do cálculo."""
        print(self.result)