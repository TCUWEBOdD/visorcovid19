# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from mapa.libreria.bd import getAuthConnection, closeConnection


class VacunasPipeline:
    """
    Modela el pipeline de procesamiento de los datos recopilados de la página de la [CCSS](https://www.ccss.sa.cr/web/coronavirus/vacunacion).
    """

    def open_spider(self, spider):
        """
        Inicia el spider abriendo la conexión a la base de datos.
        """

        self.connection = getAuthConnection()
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        """
        Cierra el spider y cierra la conexión a la base de datos.
        """

        self.cur.close()
        closeConnection(self.connection)

    def process_item(self, item, spider):
        """
        Procesa el item recopilado, guardando los datos en la base de datos.
        """

        query = """
            UPDATE datos_pais
            SET vacunas_primera_dosis = {primera_dosis},
            vacunas_segunda_dosis = {segunda_dosis}
            WHERE fecha = '{fecha}'
        """
        self.cur.execute(
            query.format(
                primera_dosis=item["primera_dosis"],
                segunda_dosis=item["segunda_dosis"],
                fecha=item["fecha"],
            )
        )
        self.connection.commit()
        return item
