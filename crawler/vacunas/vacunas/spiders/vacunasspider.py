import scrapy
from vacunas.items import VacunasItem


class VacunasSpider(scrapy.Spider):
    """
    Clase que representa el spider que recopila los datos de vacunación desde la página de la [CCSS](https://www.ccss.sa.cr/web/coronavirus/vacunacion)
    en el proceso diario de carga de datos.
    """

    name = "vacunas"
    start_urls = ["https://www.ccss.sa.cr/web/coronavirus/vacunacion"]

    def parse(self, response):
        """
        Lee la página web y obtiene los datos de cantidad de vacunas aplicadas (primera y segunda dosis) y la fecha de los datos.
        Luego el resto del pipeline continua con el procesamiento, guardando los datos recopilados en la base de datos, en la tabla ```datos_pais```.

        Parámetros
        ----------
        response
            Respuesta que carga el contenido de la página web según la URL dada en la configuración del spider.
        """

        item_primera_dosis = (
            response.css(".cifra1.bg3::text").getall()[0].replace(".", "")
        )
        item_segunda_dosis = (
            response.css(".cifra1.bg4::text").getall()[0].replace(".", "")
        )
        item_fecha = (
            response.css(
                ".actualiza.d-flex.justify-content-between.flex-column.flex-md-row p::text"
            )
            .getall()[1]
            .strip()
        )
        vacunasItem = VacunasItem(
            primera_dosis=item_primera_dosis,
            segunda_dosis=item_segunda_dosis,
            fecha=item_fecha,
        )
        yield vacunasItem
