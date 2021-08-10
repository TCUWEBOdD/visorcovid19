# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VacunasItem(scrapy.Item):
    primera_dosis = scrapy.Field()
    segunda_dosis = scrapy.Field()
    fecha = scrapy.Field()

class VacunasCNEItem(scrapy.Item):
    fecha = scrapy.Field()
    dosis = scrapy.Field()
    laboratorio = scrapy.Field()