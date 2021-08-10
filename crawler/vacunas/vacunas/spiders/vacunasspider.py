import scrapy
from vacunas.items import VacunasItem

class VacunasSpider(scrapy.Spider):
    name = 'vacunas'
    start_urls = ['https://www.ccss.sa.cr/web/coronavirus/vacunacion']

    def parse(self, response):
        item_primera_dosis = response.css('.cifra1.bg3.counter::text').getall()[0].replace(',', '')
        item_segunda_dosis = response.css('.cifra1.bg4.counter::text').getall()[0].replace(',', '')
        item_fecha = response.css('.actualiza.d-flex.justify-content-between.flex-column.flex-md-row p::text').getall()[1].strip()
        vacunasItem = VacunasItem(primera_dosis = item_primera_dosis, segunda_dosis = item_segunda_dosis, fecha = item_fecha)
        yield vacunasItem