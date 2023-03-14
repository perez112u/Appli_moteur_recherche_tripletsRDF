import tkinter as tk
from elasticsearch import Elasticsearch

# Creation de l'instance elasticsarch
es = Elasticsearch(['http://localhost:9200'])
# Création de la fenêtre
fenetre = tk.Tk()

# Définition du titre de la fenêtre
fenetre.title("Formulaire")

# Définition des étiquettes et des champs de saisie
etiquette_classe = tk.Label(fenetre, text="nom de la classe:")
etiquette_classe.pack()
champ_classe = tk.Entry(fenetre)
champ_classe.pack()

# Définition de la fonction appelée lors de l'appui sur le bouton
def rechercherGraphe():
    classe = champ_classe.get()
    print("Graphes possédant la classe " + classe + " :")
    
    # Requête de recherche sur l'index des classes pour récupérer tous les graphes qui contiennent la classe "Person"
    query = {
        "match": {
            "class_name": classe
        }
    }
    # Exécutez la requête de recherche
    res = es.search(index="classes", query=query)

    # Récupérez les graphes à partir de la réponse de recherche
    for hit in res['hits']['hits']:
        print(hit['_source']["graphs_uri"])


# Ajout du bouton
bouton_valider = tk.Button(fenetre, text="Valider", command=rechercherGraphe)
bouton_valider.pack()

# Boucle principale de l'application
fenetre.mainloop()
