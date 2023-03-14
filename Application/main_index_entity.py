from elasticsearch import Elasticsearch
import os
import glob


def add_document_to_index(entity_path, entity_name, type, graph_dir, endpoint_path):
    # recuperation de l'uri
    uri_entity = return_uri_file(entity_name.split('/')[-1])

    # recuperation du nom
    nom = uri_entity.split('/')[-1]

    # recuperation du graphe
    graph = return_uri_file(graph_dir)

    # recuperation de l'endpoint
    endpoint = return_uri_file(endpoint_path.split('/')[-1])


    # creation du nouveau document
    document = {
        "entityType": type,
        "uri": uri_entity,
        "name": nom,
        "graph": graph,
        "endpoint": endpoint,
        "labels": []
    }

    # creation de l'id du document (endpoint_graph_entity)
    id_doc = endpoint + '_' + graph + '_' + uri_entity

    # recuperation des repertoires de langues des labels
    labels_dir = os.path.join(entity_path, "labels")
    for lang_label in os.listdir(labels_dir):

        # chemin complet
        lang_label_path = os.path.join(labels_dir, lang_label)

        # recuperation des labels de la langue
        for label_name in glob.glob(lang_label_path+"/*"):
            label = label_name.split('\\')[-1]
            if label == "Christian movements":
                print (graph)
                print (type)
                print (uri_entity)
                print()
            document["labels"].append({"label": label, "lang": lang_label})
    
    es.index(index=INDEX_NAME, id=id_doc, document=document)
    return 0


def return_uri_file(file):
    file = file.replace("_", "/")
    file = file.replace("-",":")
    return file

# Créer un client Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# Définir le nom de l'index des classes
INDEX_NAME = "entities"

# Définir le mapping pour l'index classes
mappings = {
    "properties": {
        "entityType": {"type": "keyword"},
        "uri": {"type": "keyword"},
        "name": {"type": "keyword"},
        "graph": {"type": "keyword"},
        "endpoint": {"type": "keyword"},
        "labels": {
            "type": "nested",
            "properties": {
                "label": {"type": "keyword"},
                "lang": {"type": "keyword"}
            }
        }
         
    }
}

# Créer l'index avec le mapping
es.indices.delete(index=INDEX_NAME)
es.indices.create(index=INDEX_NAME, mappings=mappings)


# Parcourir les répertoire des graphes
endpoint_path = "C:/data/https-__data.open.ac.uk_query"
for graph_dir in os.listdir(endpoint_path):
    # Chemin complet
    graph_path = os.path.join(endpoint_path, graph_dir)


##########################CLASSES##########################

    # Recuperation des fichiers classes
    class_dir = os.path.join(graph_path, "classes")
    for class_name in os.listdir(class_dir):
        # Chemin complet
        entity_path_class = os.path.join(class_dir, class_name)

        # ajout du document de la classe courant dans l'index
        add_document_to_index(entity_path_class,class_name, "class", graph_dir, endpoint_path)


##########################PROPRIETES##########################

    # Recuperation des fichiers proprietes
    property_dir = os.path.join(graph_path, "properties")
    for property_name in os.listdir(property_dir):
        # Chemin complet
        entity_path_property = os.path.join(property_dir, property_name)

        # ajout du document de la propriete courante dans l'index
        add_document_to_index(entity_path_property,property_name, "property", graph_dir, endpoint_path)







    








