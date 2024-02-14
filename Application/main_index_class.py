from elasticsearch import Elasticsearch
import os
import glob

def return_uri_file(file):
    file = file.replace("_", "/")
    file = file.replace("-",":")
    return file

# Créer un client Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# Définir le nom de l'index des classes
INDEX_NAME = "graphes"

# Définir le mapping pour l'index graphes
mappings = {
    "properties": {
        "graph_id": {"type": "keyword"},
        "graph_uri": {"type": "text"},
    }
}

# # Créer l'index avec le mapping
# if not es.indices.exists(INDEX_NAME):
#     es.indices.create(index=INDEX_NAME, mappings=mappings)

#################################

# Définir le nom de l'index des classes
INDEX_NAME = "classes"

# Définir le mapping pour l'index classes
mappings = {
    "properties": {
        "class_name": {"type": "keyword"},
        "graphs_id": {"type": "keyword"}
    }
}

# Créer l'index avec le mapping
#if not es.indices.exists(INDEX_NAME):
es.indices.delete(index=INDEX_NAME)
es.indices.create(index=INDEX_NAME, mappings=mappings)


# Parcourir les répertoires des graphes
endpoint_path = "data/https-__data.open.ac.uk_query"
for graph_dir in os.listdir(endpoint_path):
    # Chemin complet
    graph_path = os.path.join(endpoint_path, graph_dir)

    class_dir = os.path.join(graph_path, "classes")
    # recuperation des fichiers classe
    for class_name in glob.glob(class_dir+"/*"):
        # recuperation du nom de la classe
        classe = class_name.split('\\')[-1].replace('.nt','')

         # Vérification si la classe est déjà présente dans l'index
        query = {
            "match": {
                "class_name": classe
            }
        }
        results = es.search(index="classes", query=query)
        if results['hits']['total']['value']>0:
            # si la classe existe deja dans l'index, on ajoute le graphe dans la liste des graphes
            class_id = results['hits']['hits'][0]['_id']
            graphs = results['hits']['hits'][0]['_source']['graphs_uri']
            graphs.append(return_uri_file(graph_dir))
            es.update(index="classes", id=class_id, body={"doc": {"graph_uris": graphs}})
        else:
            # sinon on ajoute une nouvelle classe
            result = es.index(index="classes",document={"class_name": classe, "graphs_uri": [return_uri_file(graph_dir)]})

        


