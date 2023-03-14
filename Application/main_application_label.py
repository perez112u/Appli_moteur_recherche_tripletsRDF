import tkinter as tk
from elasticsearch import Elasticsearch


# Création d'une instance de connexion à Elasticsearch
es = Elasticsearch(['http://localhost:9200'])


def search(text, entity_type="class", search_type="name", lang=''):
    if search_type == "name":
         return search_entity_by_name(text, entity_type)

    elif search_type == "label":
         return search_entity_by_label(text, entity_type, lang)
   
    else:
        raise ValueError("search_type must be 'name' or 'label'")
    


# methode permettant de chercher les document à partir d'un nom
def search_entity_by_name(name, entity_type=None):
    query = {
        "query": {
            "bool": {
                "must": [ {
                    "match": {
                        "name": name
                    }    
                }
                ]
            }
        }
    }

    if entity_type is not None:
        query["query"]["bool"]["must"].append({
            "match": {
                "entityType": entity_type
            }
        })

    results = es.search(index="entities", body=query)

    return results


# methode permettant de chercher les document à partir d'un nom de label et d'une langue si elle existe
def search_entity_by_label(label, entity_type, lang=None):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "nested": {
                            "path": "labels",
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                            "term": {
                                                f"labels.label": {
                                                    "value": label
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

    if lang != '':
        lang_query = {         
            "term": {
                f"labels.lang": {
                    "value": lang
                }
            }             
        }
        query["query"]["bool"]["must"][0]["nested"]["query"]["bool"]["must"].append({"bool": {"should": [lang_query]}})

    if entity_type is not None:
        query["query"]["bool"]["must"].append({
            "match": {
                "entityType": entity_type
            }
        })
         

    results = es.search(index="entities", body=query)

    return results





#res = search("Status", "properties", "label")
# res = search(text="ChristianTheologicalMovements", entity_type="class", search_type="name", lang="")
# for hit in res["hits"]["hits"]:
#         print(f"Nom : {hit['_source']['name']}")
#         print(f"Type d'entité : {hit['_source']['entityType']}")
#         print(f"Labels : {hit['_source']['labels']}")
#         print()




###################################################################



def on_menu_select(*args):
    if selected_option.get() == menu_options[1]:
        form_frame.pack()
    else:
        form_frame.pack_forget()

def submit():
    # Récupération des valeurs
    text_value = text_field.get()
    menu_value = selected_option.get()
    check1_value = check_var1.get()
    check2_value = check_var2.get()
    form_value = form_entries["langue"].get()

    # Affichage des valeurs dans la console
    # print("Texte:", text_value)
    # print("Menu:", menu_value)
    # print("classe:", check1_value)
    # print("propriete:", check2_value)
    # print("Formulaire:", form_value)

    # Recherche dans l'index
    if (check1_value == 1 and check2_value == 1) or (check1_value == 0 and check2_value == 0):
        types = None
    elif check1_value == 1:
        types = "class"
    elif check2_value == 1:
        types = "property"


    res = search(text=text_value, entity_type=types, search_type=menu_value, lang=form_value)
    print ("Résultat :\n")
    for hit in res["hits"]["hits"]:
        print(f"Nom : {hit['_source']['name']}")
        print(f"Type d'entité : {hit['_source']['entityType']}")
        print(f"Labels : {hit['_source']['labels']}")
        print()
    print('------------------------')


    # Réinitialisation du formulaire
    text_field.delete(0, tk.END)
    selected_option.set(menu_options[0])
    check_var1.set(0)
    check_var2.set(0)
    form_entries["langue"].delete(0, tk.END)

# Création de la fenêtre principale
root = tk.Tk()
root.title("Recherche dans graphes RDF")

# Ajustement de la taille de la fenêtre
root.geometry("400x400")

# Champ de texte
etiquette_texte = tk.Label(root, text="valeur :")
etiquette_texte.pack()
text_field = tk.Entry(root)
text_field.pack()

# Menu déroulant
etiquette_menu_recherche = tk.Label(root, text="valeur recherchée :")
etiquette_menu_recherche.pack()
menu_options = ["name", "label"]
selected_option = tk.StringVar(root)
selected_option.set(menu_options[0])
selected_option.trace("w", on_menu_select)
menu = tk.OptionMenu(root, selected_option, *menu_options)
menu.pack()

# Formulaire supplémentaire
form_frame = tk.Frame(root)

# Champ de formulaire
field_label = tk.Label(form_frame, text="Langue (optionnel) :")
field_label.pack()
field_entry = tk.Entry(form_frame)
field_entry.pack()

# Ajouter le champ de formulaire au formulaire
form_entries = {"langue": field_entry}


# Cases à cocher
etiquette_menu_type = tk.Label(root, text="rechecher dans :")
etiquette_menu_type.pack()
check_var1 = tk.IntVar()
check_var2 = tk.IntVar()
check1 = tk.Checkbutton(root, text="class", variable=check_var1)
check2 = tk.Checkbutton(root, text="property", variable=check_var2)
check1.pack()
check2.pack()

# Bouton Valider
submit_button = tk.Button(root, text="Valider", command=submit)
submit_button.pack()

# Alignement et espacement des éléments
etiquette_texte.pack(pady=10)
text_field.pack(pady=5)
etiquette_menu_recherche.pack(pady=10)
menu.pack(pady=5)
etiquette_menu_type.pack(pady=10)
check1.pack(anchor="w")
check2.pack(anchor="w")
submit_button.pack(pady=10)

# Lancement de la boucle principale
root.mainloop()