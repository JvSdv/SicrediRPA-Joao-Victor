from playwright.sync_api import sync_playwright
from src.calculoExatoWebScraper import calculoExatoWebScraper
from src.conversorDados import conversorDados

if __name__ == "__main__":
    with sync_playwright() as p:
        # 1 Faz o scraping e obtém o resultado cru
        scraper = calculoExatoWebScraper(
            valor_a_ser_atualizado=50000.0,
            data_inicial="02/04/2021",
            data_final="15/10/2024",
            indice="igpm"
        )
        scraper.start_browser(p, headless=False)
        scraper.run()
        raw_result = scraper.get_result()
        scraper.close_browser()

        # 2) Converte/parsa os dados "crus" para o formato desejado
        conversor = conversorDados(raw_result)
        conversor.run()              # Executa todos os métodos de conversão
        final_obj = conversor.get_result()  # Obtém o dicionário final

        print("\nResultado Final:")
        print(final_obj)

        # import json
        # print(json.dumps(final_obj, indent=2, ensure_ascii=False))