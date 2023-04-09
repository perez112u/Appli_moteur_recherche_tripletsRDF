from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

if es.ping():
    print ('Connexion etabli')
else:
    print('Impossible de se connecter')



index_name = "entities"

# utiliser la méthode "search" pour récupérer tous les documents de l'index
result = es.search(index=index_name, query={
		"term": {
			"graph": "https://lod.proconsortium.org/hgnc:closeMatch"
        }
    })
# result = es.get(index=index_name, id='https://sparql.proconsortium.org/virtuoso/sparql_https://lod.proconsortium.org/hgnc:closeMatch_http://purl.obolibrary.org/obo/PR_000012464')

# extraire les documents de la réponse
docs = result["hits"]["hits"]
print(result["hits"]["total"]["value"])

# parcourir les documents et afficher leur ID et leur contenu
for doc in docs:
    print(doc['_id'])
    print(doc['_source'])
    print("")


