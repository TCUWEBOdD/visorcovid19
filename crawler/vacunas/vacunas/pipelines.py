# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import psycopg2


class VacunasPipeline:
    def open_spider(self, spider):
        hostname = '163.178.101.94'
        username = 'covid'
        password = '@cov19@platfTf119!'
        database = 'covidinfo'
        port = '8080'
        self.connection = psycopg2.connect(host=hostname, port=port, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        query = """
            UPDATE datos_pais
            SET vacunas_primera_dosis = {primera_dosis},
            vacunas_segunda_dosis = {segunda_dosis}
            WHERE fecha = '{fecha}'
        """
        self.cur.execute(query.format(primera_dosis = item['primera_dosis'], segunda_dosis = item['segunda_dosis'], fecha = item['fecha']))
        self.connection.commit()
        return item
