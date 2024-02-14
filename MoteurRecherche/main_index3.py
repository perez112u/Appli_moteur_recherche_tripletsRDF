import json
from elasticsearch import Elasticsearch
import os
import glob
import hashlib


# methode pour ajouter un document en partie vide sur l'entité correspondante
def add_document_to_index(uri_entity, type, graph_dir, endpoint_path):
    # recuperation du nom
    nom = uri_entity.split('/')[-1]

    # recuperation du graphe
    graph = return_uri_file(graph_dir)

    # recuperation de l'endpoint
    endpoint = return_uri_file(endpoint_path.split('\\')[-1])


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

    # on update si le document existe, sinon on ajoute
    es.index(index=INDEX_NAME, id=id_doc, document=document)  


def add_label_to_index(uri_entity, label, lang, graph_dir, endpoint_path):
    # recuperation du graphe
    graph = return_uri_file(graph_dir)

    # recuperation de l'endpoint
    endpoint = return_uri_file(endpoint_path.split('\\')[-1])

# recuperation du l'id du document
    id_doc = endpoint + '_' + graph + '_' + uri_entity

    # label a ajouter
    new_label = {
        "label": label,
        "lang": lang
    }

    document = es.get(index=INDEX_NAME, id=id_doc)

    # Recuperation la liste "labels" du document
    labels = document['_source']['labels']

    # Ajout du nouveau label
    labels.append(new_label)

    # mettre a jour les labels du document
    es.update(index=INDEX_NAME, id=id_doc, body={"doc": {"labels":labels}})


def add_dom_prop_ran(dom, prop, ran, graph_dir, endpoint_path):
    # recuperation du graphe
    graph = return_uri_file(graph_dir)

    # recuperation de l'endpoint
    endpoint = return_uri_file(endpoint_path.split('\\')[-1])

    # recuperation des id des documents
    id_dom = endpoint + '_' + graph + '_' + dom
    id_prop = endpoint + '_' + graph + '_' + prop
    id_ran = endpoint + '_' + graph + '_' + ran

    #recuperation des noms
    dom_name = dom.split('/')[-1]
    prop_name = prop.split('/')[-1]
    ran_name = ran.split('/')[-1]


    #verfication de l existence du domain
    if es.exists(index=INDEX_NAME, id=id_dom):
            # noeaud a ajouter
            new_dom = {
                "propertyUri": prop,
                "propertyName": prop_name,
                "rangeUri": ran,
                "rangeName": ran_name
            }

            document = es.get(index=INDEX_NAME, id=id_dom)

            # Recuperation la liste "isDomainOf" du document
            isDomOf = document['_source']['isDomainOf']

            # Ajout du nouveau domain
            isDomOf.append(new_dom)

            # mettre a jour le document
            es.update(index=INDEX_NAME, id=id_dom, body={"doc": {"isDomainOf":isDomOf}})

    #verfication de l existence du property
    if es.exists(index=INDEX_NAME, id=id_prop):
            # Property a ajouter
            new_prop = {
                "domainUri": dom,
                "domainName": dom_name,
                "rangeUri": ran,
                "rangeName": ran_name
            }

            document = es.get(index=INDEX_NAME, id=id_prop)

            # Recuperation la liste "isPropertyOf" du document
            isPropOf = document['_source']['isPropertyOf']

            # Ajout du nouveau property
            isPropOf.append(new_prop)

            # mettre a jour le document
            es.update(index=INDEX_NAME, id=id_prop, body={"doc": {"isPropertyOf":isPropOf}})


    #verfication de l existence du range
    if es.exists(index=INDEX_NAME, id=id_ran):
            # Property a ajouter
            new_ran = {
                "domainUri": dom,
                "domainName": dom_name,
                "propertyUri": prop,
                "propertyName": prop_name
            }

            document = es.get(index=INDEX_NAME, id=id_ran)

            # Recuperation la liste "isPropertyOf" du document
            isRanOf = document['_source']['isRangeOf']

            # Ajout du nouveau property
            isRanOf.append(new_ran)

            # mettre a jour le document
            es.update(index=INDEX_NAME, id=id_ran, body={"doc": {"isRangeOf":isRanOf}})


def return_uri_file(file):
    file = file.replace("_", "/")
    file = file.replace("-",":")
    return file


# Créer un client Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# Définir le nom de l'index des classes
INDEX_NAME = "entities"

# si l'index n'existe pas
es.indices.delete(index=INDEX_NAME)
if not es.indices.exists(index=INDEX_NAME):
    # Définir le mapping pour l'index entities
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
    es.indices.create(index=INDEX_NAME, mappings=mappings)

exceptions = 0
labels_classe = 0
labels_property = 0
classes = 0
proprietes = 0
# Parcourir les répertoires endpoint des graphes
path = "C:/data2"

for endpoint_dir in os.listdir(path):
    endpoint_path = os.path.join(path, endpoint_dir)

    for graph_dir in os.listdir(endpoint_path):
        # Chemin complet
        graph_path = os.path.join(endpoint_path, graph_dir)

        
        # Recuperation du fichier classes.json
        if os.path.exists(graph_path + "/classes.json"):
            with open (graph_path + "/classes.json") as f:
                classes = json.load(f)

                # Recuperation de chaque classe
                for o in classes:
                    classe = o['class']
                    try:
                        add_document_to_index(classe, "class", graph_dir, endpoint_path)
                    except:
                        print ("exception")
                        exceptions += 1


        # Recuperation du fichier properties.json
        if os.path.exists(graph_path + "/properties.json"):
            with open (graph_path + "/properties.json") as f:
                properties = json.load(f)

                # Recuperation de chaque classe
                for o in properties:
                    property = o['property']
                    try:
                        add_document_to_index(property, "property", graph_dir, endpoint_path)
                    except:
                        print ("exception")
                        exceptions += 1



        # Recuperation du fichier labels_class.json
        if os.path.exists(graph_path + "/labels_class.json"):
            with open (graph_path + "/labels_class.json") as f:
                labels = json.load(f)

                # Recuperation de chaque classe
                for o in labels:
                    classe = o['class']
                    label = o['label']
                    lang = o['lang']

                    try:
                        add_label_to_index(classe, label, lang, graph_dir, endpoint_path)
                    except:
                        edp = return_uri_file(endpoint_path.split('\\')[-1])
                        g = return_uri_file(graph_dir)
                        print (f"exception label class : endpoint: {edp}, graph: {g}, class: {classe} " )
                        exceptions += 1

        
        # Recuperation du fichier labels_property.json
        if os.path.exists(graph_path + "/labels_property.json"):
            with open (graph_path + "/labels_property.json") as f:
                labels = json.load(f)

                # Recuperation de chaque classe
                for o in labels:
                    prop = o['property']
                    label = o['label']
                    lang = o['lang']

                    try:
                        add_label_to_index(prop, label, lang, graph_dir, endpoint_path)
                    except:
                        print (f"exception label property : endpoint: {endpoint_path}, graph: {graph_dir}, property: {prop} " )
                        exceptions += 1


        # Recuperation du fichier domains_properties_ranges.json
        if os.path.exists(graph_path + "/domains_properties_ranges.json"):
            with open (graph_path + "/domains_properties_ranges.json") as f:
                dom_prop_ran = json.load(f)

                # Recuperation de chaque triplet
                for o in dom_prop_ran:
                    dom = o['domain']
                    prop = o['property']
                    ran = o['range']

                    try:
                        add_dom_prop_ran(dom, prop, ran, graph_dir, endpoint_path)
                    except:
                        print (f"exception domain property range" )
                        exceptions += 1


        # Recuperation du fichier domains_properties.json
        if os.path.exists(graph_path + "/domains_properties.json"):
            with open (graph_path + "/domains_properties.json") as f:
                dom_prop = json.load(f)

                # Recuperation de chaque doublet
                for o in dom_prop:
                    dom = o['domain']
                    prop = o['property']

                    try:
                        add_dom_prop_ran(dom, prop, '', graph_dir, endpoint_path)
                    except:
                        print (f"exception domain property" )
                        exceptions += 1


        # Recuperation du fichier properties_ranges.json
        if os.path.exists(graph_path + "/properties_ranges.json"):
            with open (graph_path + "/properties_ranges.json") as f:
                dom_prop = json.load(f)

                # Recuperation de chaque doublet
                for o in dom_prop:
                    prop = o['property']
                    ran = o['range']

                    try:
                        add_dom_prop_ran('', prop, ran, graph_dir, endpoint_path)
                    except:
                        print (f"exception property range" )
                        exceptions += 1

print(f"Nombre d exception: {exceptions}")
        






    








