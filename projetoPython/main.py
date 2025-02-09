from playwright.sync_api import sync_playwright
from src.calculoExatoWebScraper import calculoExatoWebScraper

if __name__ == "__main__":
    with sync_playwright() as p:
        # Instancia a classe
        scraper = calculoExatoWebScraper(
            valor_a_ser_atualizado=50000.0,
            data_inicial="02/04/2021",
            data_final="15/10/2024",
            indice="igpm"
        )
        # Inicia o navegador com a extensão adblock na pasta "adblocker_extension"
        scraper.start_browser(p, headless=False)
        # Executa o fluxo
        scraper.run()
        # Mostra o resultado
        scraper.print_result()
        # Fecha e libera recursos
        scraper.close_browser()