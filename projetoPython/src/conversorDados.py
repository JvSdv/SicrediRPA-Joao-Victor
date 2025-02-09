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

    @staticmethod
    def parse_br_number(br_number_str: str) -> float:
        """
        Converte uma string no formato PT-BR para float
        EX: "57.005,49" => 57005.49 | "-1,93" => -1.93
        """
        s = br_number_str.strip()
        s = s.replace('.', '')   # remove pontuação de milhar
        s = s.replace(',', '.')  # transforma vírgula decimal em ponto
        return float(s)

    def parse_valor_atualizado(self):
        """
        Lê 'raw_valor_atualizado' e extrai o valor numérico.
        Ex: "Valor atualizado: R$57.005,49" => 57005.49
        """
        raw = self.data.get("raw_valor_atualizado", "")
        # Remover tudo que não seja dígito, ponto ou vírgula
        somente_numeros = re.sub(r"[^\d,\.|-]", "", raw)  # inclui possível sinal negativo
        if somente_numeros:
            try:
                self.valor_atualizado = self.parse_br_number(somente_numeros)
            except:
                self.valor_atualizado = None

    def parse_percentual_e_fator(self):
        """
        A partir de "raw_percentual_info", extrai:
          • percentual_final (float)
          • fator_multiplicacao (float)
          • meses_percentuais_raw (str) => "Abril-2021 = 1,51%; Maio-2021 = 4,10%; ..."
        """
        texto = self.data.get("raw_percentual_info", "")
        match_percentual = re.search(r"Em percentual:\s*([\d\.,-]+)%", texto) #regex
        match_fator = re.search(r"Em fator de multiplicação:\s*([\d\.,-]+)", texto)

        split_token = "Os valores do índice utilizados neste cálculo foram:"
        partes = texto.split(split_token)

        if match_percentual and match_fator and len(partes) > 1:
            # Ex: "14,0110"
            percentual_str = match_percentual.group(1).strip()
            # Ex: "1,140110"
            fator_str = match_fator.group(1).strip()

            # Este pedaço é "Abril-2021 = 1,51%; Maio-2021 = 4,10%; ..."
            meses_info = partes[1].strip()

            try:
                self.percentual_final = self.parse_br_number(percentual_str)
                self.fator_multiplicacao = self.parse_br_number(fator_str)
                self.meses_percentuais_raw = meses_info
            except:
                self.percentual_final = None
                self.fator_multiplicacao = None
                self.meses_percentuais_raw = None

    def find_menor_maior_percentual(self):
        """
        Cria um dicionário auxiliar { "Abril-2021": 1.51, ... } para encontrar
        menor e maior valor. Popula self.menor_percentual e self.maior_percentual
        com strings do tipo "Mês-Ano = X,XX%".
        """
        if not self.meses_percentuais_raw:
            return

        # 1) Transformar em lista
        itens = [elem.strip() for elem in self.meses_percentuais_raw.split(";") if elem.strip()]

        # Ex: "Abril-2021 = 1,51%" # evitar complexidade 
        aux_dict = {}
        for it in itens:
            if "=" in it:
                mes, val = it.split("=")
                mes = mes.strip()  # "Abril-2021"
                val = val.strip()  # "1,51%"
                # Remover '%' e espaços
                val_clean = val.replace("%", "").strip()
                # Tentar converter
                try:
                    numeric_val = self.parse_br_number(val_clean)
                    aux_dict[mes] = numeric_val
                except:
                    pass

        if not aux_dict:
            return

        # Encontrar menor e maior
        menor_mes = min(aux_dict, key=aux_dict.get)  # string
        maior_mes = max(aux_dict, key=aux_dict.get)

        # Reconstruir no mesmo estilo "mes-ano = X,XX%"
        menor_val_str = str(aux_dict[menor_mes]).replace(".", ",")
        maior_val_str = str(aux_dict[maior_mes]).replace(".", ",")

        self.menor_percentual = f"{menor_mes} = {menor_val_str}%"
        self.maior_percentual = f"{maior_mes} = {maior_val_str}%"

    def run(self):
        """
        Executa todos os passos de conversão e preenche self.final_result
        com o dicionário final.
        """
        # 1) Extrair valor atualizado
        self.parse_valor_atualizado()

        # 2) Extrair percentual_final, fator_multiplicacao e meses_percentuais
        self.parse_percentual_e_fator()

        # 3) Encontrar menor e maior percentual
        self.find_menor_maior_percentual()

        # 4) Montar o objeto final com as formatações desejadas
        #    Abaixo, transformamos em string com formatações (casas decimais, etc.)
        #    ou retornamos como float — depende da sua necessidade.
        retorno_da_consulta = bool(self.data.get("retornoDaConsulta", False))
        valor_informado = float(self.data.get("valorInformado", 0.0))

        # Fator vamos representar com vírgula + 6 casas
        fator_str = ""
        if self.fator_multiplicacao is not None:
            # Converte p/ "1.140110" e então substitui . por ,
            fator_str = f"{self.fator_multiplicacao:.6f}".replace(".", ",")

        # Meses em lista do jeito que veio, só removendo vazios
        meses_list = []
        if self.meses_percentuais_raw:
            meses_list = [m.strip() for m in self.meses_percentuais_raw.split(";") if m.strip()]

        self.final_result = {
            "retornoDaConsulta": retorno_da_consulta,
            "valorInformado": f"{valor_informado:.2f}",
            "dataInicial": self.data.get("dataInicial", ""),
            "dataFinal": self.data.get("dataFinal", ""),
            "indice": self.data.get("indice", ""),
            "valorAtualizado": f"{self.valor_atualizado:.2f}" if self.valor_atualizado else None,
            "percentualFinal": f"{self.percentual_final:.4f}" if self.percentual_final else None,
            "fatorMultiplicacao": fator_str if fator_str else None,
            "mesesPercentuais": meses_list,
            "menorPercentual": self.menor_percentual,
            "maiorPercentual": self.maior_percentual
        }

    def get_result(self):
        return self.final_result

    def print_result(self):
        """Se desejar imprimir o objeto final no console, use este método."""
        print(self.final_result)