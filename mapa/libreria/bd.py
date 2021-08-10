import psycopg2 as psql
        
POSTGRES = 'covid'
PASS = '@cov19@platfTf119!'
HOST = "127.0.0.1"
PORT = "8080"
BD = "covidinfo"

def getConnection(user, password, host, port, db):
    connection = psql.connect(user = user,  password = password,
                    host = host, port = port, database = db)
    
    return connection
	
def getMyConnection():
	return getConnection(POSTGRES, PASS, HOST, PORT, BD)

def closeConnection(connection):
    if connection != None:
        connection.close()



# forma de cargar un custom 
#pg_restore -U covid -d covidinfo2 covid_project-18-10-2020-S.sql
#ogr2ogr -f "PostgreSQL" PG:"host=172.16.9.69 dbname='covidinfo2' user='covid' password='C0vv111d!!'" "C:\Users\diego\Dropbox\Public\paradas.geojson"
