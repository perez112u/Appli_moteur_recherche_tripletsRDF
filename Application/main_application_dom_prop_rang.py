import tkinter as tk
from elasticsearch import Elasticsearch


# Création d'une instance de connexion à Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# chercher les domaines et rang correspondant à une propriete donnee
def search_dom_rang_with_property(property_name):
    # requête Elasticsearch pour récupérer les documents correspondant au nom de propriété donné
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "entityType": "property"
                        }
                    },
                    {
                        "match": {
                            "name": property_name
                        }
                    }
                ]
            }
        }
    }
    res = es.search(index="entities", body=query)

    # traitement des résultats
    entities = []
    print(res['hits']['total']["value"])
    for hit in res['hits']['hits']:
        entity = hit['_source']

        # récupération des domaines et ranges pour chaque isPropertyOf
        for is_property_of in entity['isPropertyOf']:
            domain = is_property_of['domainUri']
            range = is_property_of['rangeUri']
            entities.append((domain, range))

    return entities



# cherche les proprietes correspondant à un domaine et rang donnee
def search_prop_with_dom_ran(domain, range):
    # requête Elasticsearch pour récupérer les documents correspondant au nom de propriété donné
    query = {
        "query": {
            "bool": {
                "must": [
                     {
                        "nested": {
                            "path": "isPropertyOf",
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                            "term": {
                                                "isPropertyOf.domainName": {
                                                    "value": domain
                                                }
                                            }
                                        },
                                        {
                                            "term": {
                                                "isPropertyOf.rangeName": {
                                                    "value": range
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

    res = es.search(index="entities", body=query)

    # traitement des résultats
    entities = []
    print(res['hits']['total']["value"])
    for hit in res['hits']['hits']:
        entity = hit['_source']['uri']
        entities.append(entity)

    return entities



# cherche range a partir d'un domain et d une property
def search_rang_with_dom_prop(domain, property):
    # requête Elasticsearch pour récupérer les documents correspondant au nom de propriété donné
    query = {
        "query": {
            "bool": {
                "must": [
                     {
                        "nested": {
                            "path": "isRangeOf",
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                            "term": {
                                                "isRangeOf.domainName": {
                                                    "value": domain
                                                }
                                            }
                                        },
                                        {
                                            "term": {
                                                "isRangeOf.propertyName": {
                                                    "value": property
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

    res = es.search(index="entities", body=query)

    # traitement des résultats
    entities = []
    print(res['hits']['total']["value"])
    for hit in res['hits']['hits']:
        entity = hit['_source']['uri']
        entities.append(entity)

    return entities



# cherche domain a partir d'une property et d un range
def search_domain_with_prop_rang(property, range):
    # requête Elasticsearch pour récupérer les documents correspondant au nom de propriété donné
    query = {
        "query": {
            "bool": {
                "must": [
                     {
                        "nested": {
                            "path": "isDomainOf",
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                            "term": {
                                                "isDomainOf.propertyName": {
                                                    "value": property
                                                }
                                            }
                                        },
                                        {
                                            "term": {
                                                "isDomainOf.rangeName": {
                                                    "value": range
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

    res = es.search(index="entities", body=query)

    # traitement des résultats
    entities = []
    print(res['hits']['total']["value"])
    for hit in res['hits']['hits']:
        entity = hit['_source']['name']
        entities.append(entity)

    return entities



# cherche property et range a partir d un domain
def search_prop_rang_with_domain(domain):
    # requête Elasticsearch pour récupérer les documents correspondant au nom de propriété donné
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "name": domain
                        }
                    }
                ]
            }
        }
    }

    res = es.search(index="entities", body=query)

    # traitement des résultats
    property_range = []
    print(res['hits']['total']["value"])
    for hit in res['hits']['hits']:
        for isDom in hit["_source"]["isDomainOf"]:
            prop = isDom["propertyUri"]
            ran = isDom["rangeUri"]
            property_range.append({"property": prop, "range": ran})
                             
    return property_range



# cherche domain et property a partir d un range
def search_dom_prop_with_rang(range):
    # requête Elasticsearch pour récupérer les documents correspondant au nom de propriété donné
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "name": range
                        }
                    }
                ]
            }
        }
    }

    res = es.search(index="entities", body=query)

    # traitement des résultats
    property_range = []
    print(res['hits']['total']["value"])
    for hit in res['hits']['hits']:
        for isRan in hit["_source"]["isRangeOf"]:
            dom = isRan["domainUri"]
            prop = isRan["propertyUri"]
            property_range.append({"domain": dom, "property": prop})
                             
    return property_range











########################################################

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        # Création des cases à cocher
        self.checkbox_frame = tk.Frame(self.master)
        self.checkbox_frame.pack(side="top", padx=10, pady=10)
        self.check_var1 = tk.BooleanVar(value=False)
        self.check_var2 = tk.BooleanVar(value=False)
        self.check_var3 = tk.BooleanVar(value=False)
        self.check_button1 = tk.Checkbutton(self.checkbox_frame, text="Domain", variable=self.check_var1, command=self.update_form)
        self.check_button2 = tk.Checkbutton(self.checkbox_frame, text="Property", variable=self.check_var2, command=self.update_form)
        self.check_button3 = tk.Checkbutton(self.checkbox_frame, text="Rang", variable=self.check_var3, command=self.update_form)
        self.check_button1.pack(side="left")
        self.check_button2.pack(side="left")
        self.check_button3.pack(side="left")

        # Création du formulaire
        self.form_frame = tk.Frame(self.master)
        self.form_frame.pack(side="top", padx=10, pady=10)
        self.label1 = tk.Label(self.form_frame, text="Domain")
        self.label2 = tk.Label(self.form_frame, text="Property")
        self.label3 = tk.Label(self.form_frame, text="Rang")
        self.entry1 = tk.Entry(self.form_frame)
        self.entry2 = tk.Entry(self.form_frame)
        self.entry3 = tk.Entry(self.form_frame)
        self.entry1.config(state="disabled")
        self.entry2.config(state="disabled")
        self.entry3.config(state="disabled")
        self.label1.grid(row=0, column=0, sticky="w")
        self.label2.grid(row=1, column=0, sticky="w")
        self.label3.grid(row=2, column=0, sticky="w")
        self.entry1.grid(row=0, column=1, padx=10, pady=5)
        self.entry2.grid(row=1, column=1, padx=10, pady=5)
        self.entry3.grid(row=2, column=1, padx=10, pady=5)

        # Création du bouton de validation
        self.submit_button = tk.Button(self.master, text="Valider", command=self.submit)
        self.submit_button.pack(side="bottom", padx=10, pady=10)

    def update_form(self):
        # Mise à jour de l'état des champs du formulaire en fonction des cases à cocher
        if self.check_var1.get():
            self.label1.config(state="normal")
            self.entry1.config(state="normal")
        else:
            self.label1.config(state="disabled")
            self.entry1.config(state="disabled")

        if self.check_var2.get():
            self.label2.config(state="normal")
            self.entry2.config(state="normal")
        else:
            self.label2.config(state="disabled")
            self.entry2.config(state="disabled")

        if self.check_var3.get():
            self.label3.config(state="normal")
            self.entry3.config(state="normal")
        else:
            self.label3.config(state="disabled")
            self.entry3.config(state="disabled")

    def submit(self):
        # Affichage des données du formulaire et de l'état des cases
        print("Case 1: ", self.check_var1.get())
        print("Case 2: ", self.check_var2.get())
        print("Case 3: ", self.check_var3.get())
        print ("Champ 1 : ", self.entry1.get())
        print ("Champ 2 : ", self.entry2.get())
        print ("Champ 3 : ", self.entry3.get())

        if self.entry1.get() == '' and self.entry2.get() != '' and self.entry3.get() == '':
            results = search_dom_rang_with_property(self.entry2.get())
            print ("Propriete : " + self.entry2.get())
            for res in results:
                print ("-------")
                print ("Domain : " + res[0] + " / Rang : " + res[1])
        
        elif self.entry1.get() != '' and self.entry2.get() == '' and self.entry3.get() != '':
            results = search_prop_with_dom_ran(self.entry1.get(), self.entry3.get())
            print ("Proprietes liant " + self.entry1.get() + " --> ? --> " + self.entry3.get() + " :")
            for res in results:
                print ("----------")
                print ("Propriete : " + res)

        elif self.entry1.get() != '' and self.entry2.get() != '' and self.entry3.get() == '':
            results = search_rang_with_dom_prop(self.entry1.get(), self.entry2.get())
            print ("Range de " + self.entry1.get() + " --> " + self.entry2.get() + ' --> ? :')
            for res in results:
                print ("----------")
                print ("Range : " + res)

        elif self.entry1.get() == '' and self.entry2.get() != '' and self.entry3.get() != '':
            results = search_domain_with_prop_rang(self.entry2.get(), self.entry3.get())
            print ("Domain de ? --> " + self.entry2.get() + " --> " + self.entry3.get())
            for res in results:
                print ("----------")
                print ("Domain : " + res)

        elif self.entry1.get() != "" and self.entry2.get() == "" and self.entry3.get() == '':
            results = search_prop_rang_with_domain(self.entry1.get())
            print ("Property et Range de " + self.entry1.get() + " --> " + "?" + ' --> ? :')
            for res in results:
                print ('----------')
                print ("Property --> Range : " + res["property"] + " --> " + res["range"])

        elif self.entry1.get() == "" and self.entry2.get() == "" and self.entry3.get() != '':
            results = search_dom_prop_with_rang(self.entry3.get())
            print ("Domain et Property de " + "?" + " --> " + "?" + ' --> ' + self.entry3.get() + ' :')
            for res in results:
                print ('----------')
                print ("Domain --> Property : " + res["domain"] + " --> " + res["property"])



                






root = tk.Tk()
app = Application(master=root)
app.mainloop()
