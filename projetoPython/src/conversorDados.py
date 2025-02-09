import re

class conversorDados:
    """
    Converte os dados crus do dicionário vindo do calculoExatoWebScraper
    em um dicionário final com tipos e formatações desejadas.
    """
    def __init__(self, result_dict: dict):
        # Estrutura esperada (antes do parse):
        # {
        #   "retornoDaConsulta": bool,
        #   "valorInformado": float,
        #   "dataInicial": str,
        #   "dataFinal": str,
        #   "indice": str,
        #   "raw_valor_atualizado": "Valor atualizado: R$57.005,49",
        #   "raw_percentual_info": "Em percentual: 14,0110% ...
        #                          Em fator de multiplicação: 1,140110 ...
        #                          Os valores do índice utilizados neste cálculo foram: ...",
        # }
        self.data = result_dict

        # Estes atributos serão populados durante as conversões
        self.valor_atualizado = None
        self.percentual_final = None
        self.fator_multiplicacao = None
        self.meses_percentuais_raw = None  # texto completo, ex: "Abril-2021 = 1,51%; Maio-2021 = 4,10%; ..."
        self.menor_percentual = None
        self.maior_percentual = None

        # Objeto final a ser retornado
        self.final_result = {}

