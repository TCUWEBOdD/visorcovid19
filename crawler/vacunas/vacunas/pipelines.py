# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from mapa.libreria.bd import getAuthConnection, closeConnection


class VacunasPipeline:
    def open_spider(self, spider):
        self.connection = getAuthConnection()
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        self.cur.close()
        closeConnection(self.connection)

    def process_item(self, item, spider):
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
