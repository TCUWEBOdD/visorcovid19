# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VacunasItem(scrapy.Item):
    """
    Objeto que representa los datos a recopilar de la página de vacunación de la [CCSS](https://www.ccss.sa.cr/web/coronavirus/vacunacion).
    Se recopila la cantidad de primeras dosis aplicadas, segundas dosis aplicadas y la fecha de los datos.
    """

    primera_dosis = scrapy.Field()
    segunda_dosis = scrapy.Field()
    fecha = scrapy.Field()
