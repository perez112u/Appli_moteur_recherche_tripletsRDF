import json
from elasticsearch import Elasticsearch
import os
import glob
import hashlib


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
        "labels": [],
        "isPropertyOf": [],
        "isDomainOf": [],
        "isRangeOf": []
    }

    # creation de l'id du document (endpoint_graph_entity)
    id_doc = endpoint + '_' + graph + '_' + uri_entity
   # id_doc = hashlib.sha256(id.encode())

    # recuperation des repertoires de langues des labels
    labels_dir = os.path.join(entity_path, "labels")
    for lang_label in os.listdir(labels_dir):

        # chemin complet
        lang_label_path = os.path.join(labels_dir, lang_label)

        # recuperation des labels de la langue
        for label_name in glob.glob(lang_label_path+"/*"):
            label = label_name.split('\\')[-1]
            document["labels"].append({"label": label, "lang": lang_label})


    # recuperation du fichier isPropertyOf
    is_prop_file = os.path.join(entity_path,"is_property_of.json")
    if os.path.exists(is_prop_file):
        with open (is_prop_file, "r") as f:
            for line in f:
                val = json.loads(line)
                if "domain" in val and "range" in val:
                    domain, range = val["domain"], val["range"]
                    document["isPropertyOf"].append({"domainUri": domain, "domainName": domain.split("/")[-1], "rangeUri": range, "rangeName": range.split('/')[-1]})


    # recuperation du fichier isDomainOf
    is_dom_file = os.path.join(entity_path,"is_domain_of.json")
    if os.path.exists(is_dom_file):
        with open (is_dom_file, "r") as f:
            for line in f:
                val = json.loads(line)
                if "property" in val and "range" in val:
                    property, range = val["property"], val["range"]
                    document["isDomainOf"].append({"propertyUri": property, "propertyName": property.split("/")[-1], "rangeUri": range, "rangeName": range.split('/')[-1]})



    # recuperation du fichier isRangeOf
    is_range_file = os.path.join(entity_path,"is_range_of.json")
    if os.path.exists(is_range_file):
        with open (is_range_file, "r") as f:
            for line in f:
                val = json.loads(line)
                if "domain" in val and "property" in val:
                    domain, property = val["domain"], val["property"]
                    document["isRangeOf"].append({"domainUri": domain, "domainName": domain.split("/")[-1], "propertyUri": property, "propertyName": property.split('/')[-1]})
                    

    
    print (document)
    print ("------------")
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
    },
    "isPropertyOf": {
        "type": "nested",
        "properties": {
            "domainUri": {"type": "keyword"},
            "domainName": {"type": "keyword"},
            "rangeUri": {"type": "keyword"},
            "rangeName": {"type": "keyword"}
        }
    },
    "isDomainOf": {
        "type": "nested",
        "properties": {
            "propertyUri": {"type": "keyword"},
            "propertyName": {"type": "keyword"},
            "rangeUri": {"type": "keyword"},
            "rangeName": {"type": "keyword"}
        }
    },
    "isRangeOf": {
        "type": "nested",
        "properties": {
            "domainUri": {"type": "keyword"},
            "domainName": {"type": "keyword"},
            "propertyUri": {"type": "keyword"},
            "propertyName": {"type": "keyword"}
        }
    }   
}

}

# Créer l'index avec le mapping
es.indices.delete(index=INDEX_NAME)
es.indices.create(index=INDEX_NAME, mappings=mappings)


# Parcourir les répertoire des graphes
endpoint_path = "C:/data/http-__dbpedia.org_sparql"
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







    








