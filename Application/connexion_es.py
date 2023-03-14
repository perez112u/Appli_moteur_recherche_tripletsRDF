from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

if es.ping():
    print ('Connexion etabli')
else:
    print('Impossible de se connecter')



index_name = "entities"

query = {"query": {"match_all": {}}}

# Utilisez la méthode search pour exécuter la requête et récupérer toutes les données
results = es.search(index=index_name, body=query, size=10000)

# Parcourez les résultats et affichez les données
for hit in results["hits"]["hits"]:
    print(hit["_source"])


