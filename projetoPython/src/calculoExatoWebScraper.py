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
        self.valor_a_ser_atualizado = valor_a_ser_atualizado
        self.data_inicial = data_inicial  # Formato "dd/mm/aaaa"
        self.data_final = data_final      # Formato "dd/mm/aaaa"
        self.indice = indice              # Ex: "igpm", "ipca", etc.

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

