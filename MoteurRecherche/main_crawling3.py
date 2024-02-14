import json
import math
import os
import shutil
import time
import warnings
from urllib import error
from SPARQLWrapper import SPARQLExceptions
from SPARQLWrapper import SPARQLWrapper, JSON

# internal modules
from latex import Latex

"""""""""""""""""""""""""""""""""""""""""""""""""""CLASS_QUERY"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Query:
    """
    Object launched in a SPARQL query with editable parameters
    :ivar name: name of the SPARQL file
    :type name: str
    :ivar uri: SPARQL endpoint's URI
    :type uri: str
    :ivar graph: graph's URI targeted in the SPARQL endpoint
    :type graph: str
    :ivar content: SPARQL query's instructions, except the limit and the offset
    :type content: str
    :ivar iteration: number of query's iterations
    :type iteration: int
    :ivar limit: parameter LIMIT in the SPARQL query
    :type limit: int
    :ivar offset: parameter OFFSET in the SPARQL query
    :type limit: int
    :ivar search_graph: True, if the query searches for a graph's list in a SPARQL endpoint, else False
    :type search_graph : boolean
    """

    def __init__(self):
        """
            Initializes all the necessary attributes for a query object
        """
        self.name = ""
        self.uri = ""
        self.graph = ""
        self.content = ""
        self.iteration = 0
        self.limit = 0
        self.offset = 0
        self.search_graph = False

    def set_content(self, file):
        """
        Constructs the content of a query object from a SPARQL file
        :param file : file.sparql with a string of SPARQL instructions
        :type file : str
        """
        self.content = ""
        with open(file, 'r', encoding='utf-8') as fi:
            for line in fi:
                line = line.replace("\n", " ").strip("\'")
                self.content += line
        return self.content

    def set_limit(self, nb):
        """
        Defines the limit of a query object
        :param nb : the number of results wanted in a query
        :type nb : int
        """
        self.limit = nb
        self.content = self.content.replace(f"LIMIT 0", f"LIMIT {nb}")

    def set_offset(self, nb):
        """
        Defines the offset of a query object in attribute content
        :param nb : the step where the query begins to run for results
        :type nb : int
        """
        self.offset = nb
        self.content = self.content.replace(f"OFFSET 0", f"OFFSET {nb}")

    def next_offset(self, prec, succ):
        """
        Writes the next offset of a query object from its predecessor in attribute content
        :param prec : previous offset value
        :type prec : int
        :param succ : new offset value
        :type succ : int
        """
        self.offset = succ
        self.content = self.content.replace(f"OFFSET {prec}", f"OFFSET {succ}")

    def no_limit(self):
        """
        Defines no limit in a query object in attribute content
        value -1 is for display : indicates no limit
        """
        self.limit = -1
        self.content = self.content.replace(f"LIMIT 0", f"")

    def no_offset(self):
        """
        Defines no offset in  a query object in attribute content
        value -1 is for display : indicates no offset
        """
        self.offset = -1
        self.content = self.content.replace(f"OFFSET 0", f"")

    def header_graph(self, graph):
        """
        Writes the graph in the query object in attribute content
        :param graph: name of a graph that will be targeted
        :type graph: str
        """
        self.content = self.content.replace(f"<.>", f"<{graph}>")


"""""""""""""""""""""""""""""""""""""""""""""""LOG_FONCTIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"""
Global variables to fill in the latex report all along the process
All this variables are dictionaries
-----------------------------------------------------------------------------------------------------------------------
report_query_graph : stores the 3 queries to get graphs in endpoints and their results
report_each_query_section : stores each SPARQL query and its unique results of a SPARQL endpoint
report_errors_section : stores all errors encountered during getting results of a SPARQL endpoint
report_partition : stores information about a potential partition of SPARQL query results
report_subpartition: stores information about a potential subpartition of SPARQL query results
"""

report_query_graph = {}
report_each_query_section = {}
report_errors_section = {}
report_partition = {}
report_subpartition = {}


def generate_report(endpoint, more_res, l_graph, dis_res, invalid_json, partition) -> None:
    """
    generate a latex document by default report.tex about all events by getting results from endpoint
    :param endpoint: SPARQL uri endpoint
    :type endpoint: str
    :param more_res: SPARQL graph query with most results in endpoint
    :type more_res: tuple - (number of results, query)
    :param l_graph: graphs that have been found in endpoint
    :type l_graph: list
    :param dis_res: total amount of distinct results found in endpoint
    :type dis_res: int
    :param invalid_json : string results that couldn't be converted back into json properly
    :type invalid_json: list
    :param partition : indicates if json results needed to be divided in parts or not
    :type partition: bool
    """
    title = f"Report on querying Sparql endpoints"
    doc_name = "report.tex"
    Latex.create_log_document(doc_name, title)
    note = open(doc_name, "a", encoding="utf-8")

    # report - note about the endpoint requested
    note.write(Latex.part(Latex.format_special_char("Sparql Endpoint : " + endpoint)))
    # report - graphs researched
    note.write(Latex.section("Graphs research"))

    # report - all results about graphs search
    note.write(Latex.subsection("Queries for graphs and results"))
    query = more_res[1].replace("query/", "")
    if report_query_graph == {}:
        note.write(Latex.format_special_char(f"No exploitable results"))
    else:
        for graph, res in report_query_graph.items():
            graph = graph.replace("query/", "")
            note.write(Latex.format_special_char(f"graph {graph} : {res} results \n"))
            note.write(Latex.newline())
        if len(more_res) == 2:
            note.write(Latex.format_special_char(Latex.bold(f"{query} returns more results ({more_res[0]})\n")))

    # report - list of graphs
    if len(more_res) == 2:
        note.write(Latex.subsection(Latex.format_special_char(f"List of graphs selected")))
        k = 1
        for graph in l_graph:
            note.write(Latex.format_special_char(f"graph {k} - {graph} \n"))
            note.write(Latex.newline())
            k += 1
    else:
        note.write(Latex.subsection(Latex.format_special_char(f"Graphs on {endpoint}")))
        note.write(Latex.format_special_char(f"No list of graphs"))
    note.write(Latex.next_page())

    # report - querying endpoint
    note.write(Latex.section(Latex.format_special_char(f"Querying {endpoint}")))
    note.write(Latex.subsection("Results by query"))

    # report - note about each query and its results
    for key, value in report_each_query_section.items():
        key = key.replace("query/", "")
        note.write(Latex.format_special_char(f"Query {key} - distinct results : {value}\n"))
        note.write(Latex.newline())
    note.write(Latex.format_special_char(Latex.bold(f"Total of unique results found {dis_res} on {endpoint} \n")))

    # report - all errors during the process
    note.write(Latex.subsection("Error Log"))
    if report_errors_section == {}:
        note.write("No errors encountered during the process \n")
    else:
        note.write(Latex.itemize_begin())
        for graph, problem in report_errors_section.items():
            note.write(Latex.item())
            note.write(str(graph))
            note.write(str(problem))
        note.write(Latex.itemize_end())
    note.write(Latex.itemize_begin())
    note.write(Latex.item())
    note.write(f"Number of errors : {len(report_errors_section)}" + "\n")
    note.write(Latex.itemize_end())

    # report - about all processes before indexation
    note.write(Latex.next_page())
    note.write(Latex.section("Process before indexation"))

    # about string results fail to be converted back to json results (after distinct operation)
    note.write(Latex.subsection("JSON results conversion after distinct operation"))
    if invalid_json:
        note.write("An error has occurred while converting back string results to json results\n")
        note.write(Latex.itemize_begin())
        for elem in invalid_json:
            note.write(Latex.item())
            note.write(str(elem))
        note.write(Latex.itemize_end())
    else:
        note.write(Latex.format_special_char("All string results were converted into valid json results\n"))

    # about results partitions
    note.write(Latex.subsection("Partition in separated queries"))
    if partition is True:
        note.write("Results volume is superior to 2 millions and has been split into partitions\n")
        note.write(Latex.itemize_begin())
        for info, value in report_partition.items():
            note.write(Latex.item())
            note.write(Latex.format_special_char(f"{info} {value}"))
        note.write(Latex.itemize_end())
        note.write("These partitions are bulked separately and merged into same index")
    else:
        note.write(f"The volume of {dis_res} results does not need any partition\n")

    # report - about indexation
    note.write(Latex.next_page())
    note.write(Latex.section("Elastic Search Indexation"))
    note.close()

""""""""""""""""""""""""""""""""""""""""""""""QUERY_FONCTIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    

def setting_query(file, endpoint, graph, limit, target_graph):
    """ Creates an object Query with all the attributes that need to be edited
    :param file : name of the sparql file
    :type : str
    :param endpoint : SPARQL endpoint URI
    :type : str
    :param graph : endpoint's graph URI
    :type : str
    :param limit : number of results wanted
    :type : int
    :param target_graph : True, if the query aims to search a graph's list, else False
    :type : bool
    :return a ready-to-use Query Object
    """
    q = Query()
    q.name = file
    q.uri = endpoint
    q.graph = graph
    q.set_content(file)
    q.header_graph(graph)
    q.set_limit(limit)
    q.search_graph = target_graph
    return q


def setting_sparql(uri, time_out, returned_format, sparql_instructions):
    """ Set the SPARQL query through SPARQL Wrapper
    :param uri : SPARQL endpoint URI
    :type : str
    :param time_out : time given to reach out the server
    :type : int
    :param returned_format : the results format awaited
    :type : str
    :param sparql_instructions: the query's instructions sent to server
    :type : str
    :return a ready-to-use SPARQLWrapper Object
    """
    sparql = SPARQLWrapper(uri)
    sparql.setTimeout(time_out)
    sparql.setReturnFormat(returned_format)
    sparql.setQuery(sparql_instructions)
    return sparql


# launch a sparql query on an endpoint
def launch_query(q, k):
    """ Launches a SPARQL query
    :param q: a Query Object
    :type q : Query
    :param k: graph number targeted in the query
    :return: results, number of results, and if necessary the name of the query
    """

    try:
        q.no_limit(), q.no_offset()
        sparql = setting_sparql(q.uri, 3600, JSON, q.content)

        # sending and getting converted results in json - counting raw results founded
        res = sparql.queryAndConvert()
        nb_res = count_results(res)

        # activate the filter to catch a warning as an exception
        warnings.filterwarnings("error")

        # displaying raw results of any query (of graphs, of json results)
        if q.search_graph is False:
            pass
            # print(f"endpoint : {q.uri} requete : {q.name} graph {k} {q.graph} raw results : {nb_res}")
        else:
            print(f"endpoint : {q.uri} requete : {q.name} raw results : {nb_res}")
        return nb_res, q.name, res

    # all errors catched that can occur in the process of getting json results
    # - Runtime warnings from (Sparql) Wrapper file
    # - HTTP Errors
    # - Specific Exceptions from SPARQL (Wrapper) Exceptions file
    # - other miscellaneous exceptions
    # returns empty and null values
    except RuntimeWarning as run:
        report_errors_section["RuntimeWarning : "] = Latex.format_special_char(str(run))
        return 0, "", {}
    except error.HTTPError as ehttp:
        print(ehttp)
        if q.search_graph is False:
            key = Latex.format_special_char(f"Error on {q.name} graph {k} {q.graph} : ")
        else:
            key = Latex.format_special_char(f"Error on  {q.name} : ")
        report_errors_section[key] = Latex.format_special_char(str(ehttp))
        return 0, "", {}
    except Exception as e:
        if isinstance(e, SPARQLExceptions.EndPointInternalError) or \
                isinstance(e, SPARQLExceptions.EndPointNotFound) or \
                isinstance(e, SPARQLExceptions.URITooLong) or \
                isinstance(e, SPARQLExceptions.QueryBadFormed) or \
                isinstance(e, SPARQLExceptions.Unauthorized):
            print(e.args)
            errors = Latex.clean_error_wrapper(e.args[0])
            if q.search_graph is False:
                key = Latex.format_special_char(f"Error on graph {q.graph} {q.name} : ")
            else:
                key = Latex.format_special_char(f"Error on  {q.name} : ")
            value = Latex.format_special_char(f"{errors[0]} \n {errors[1]}")
            report_errors_section[key] = value
            return 0, "", {}
        else:
            print(e)
            report_errors_section[e] = str(e.args)
            return 0, "", {}


""""""""""""""""""""""""""""""""""""""""""""""RESULTS_FONCTIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def display_results(res) -> None:
    """
    displays results of a sparql query, either a json dict or json list
    :param res: json results or results
    :type res : dict or list
    """
    i = 0
    if isinstance(res, dict):
        for r in res["results"]["bindings"]:
            print(f"res {i + 1}", r)
            i += 1
    elif isinstance(res, list):
        for elem in res:
            print(f"res {i + 1}", elem)
            i += 1


def count_results(res):
    """
    counts results of a sparql query, either a json dict or json list
    :param res: json results
    :type res: dict
    :return: number of results
    """
    i = 0
    if isinstance(res, dict):
        for _ in res["results"]["bindings"]:
            i += 1
    return i

""""""""""""""""""""""""""""""""""""""""""""""GRAPH_FONCTIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def extract_graph(dic, endp):
    """
    displays the graph query with most results on an SPARQL endpoint
    extracts a graph list from the SPARQL endpoint
    :param dic: graph sets
    :type dic: dict
    :param endp: SPARQL endpoint URI
    :type endp : str
    :return: a list of graphs names for the query with the most results, and the query itself
    """

    def graphset_with_more_results(d):
        """
        determines the graph set with more results
        a graph set is a tuple returned by a sparql query (number of results, query name, json result)
        :param d: graph sets
        :type d: dict
        :return: a tuple of (the highest number of results, its query name, its json results)
        """
        maxi = 0
        for k in d:
            if k >= maxi:
                maxi = k
        return maxi, d[maxi][0], d[maxi][1]

    def listing_graph(res):
        """
        creates a graph list from a json result, from a graph query sent to SPARQL endpoint
        :param res: json results
        :type res: dict
        :return: a list of graphs names
        """
        l_graph = []
        for r in res["results"]["bindings"]:
            for k, val in r.items():
                for s_key, s_val in val.items():
                    graph = s_val
                    if graph != 'uri':
                        graph = graph.strip(',')
                        l_graph.append(graph)
        return l_graph

    try:
        max_res = graphset_with_more_results(dic)
        if max_res != ((),):
            print(f"endpoint {endp} : more results ({max_res[0]}) for {max_res[1]}\n")

            # report - store the query with a maximum results
            more_result_query = max_res[0], max_res[1]

            return listing_graph(max_res[2]), more_result_query
        else:
            print("no corresponding query to get a graphs list")
    except Exception as e:
        key = "Error while getting graphs list or query with most results \n"
        report_errors_section[key] = f" {e} as a result"
        print("An error has occurred to get graphs list and/or query with most results")





""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def return_file_uri(uri):
    uri = uri.replace("/", "_")
    uri = uri.replace(":","-")
    return uri



def main():

    list_endpoint = ["https://data.open.ac.uk/query", "https://sparql.nextprot.org/", "http://rdf.disgenet.org/sparql/",
                     "https://genome.microbedb.jp/sparql", "https://id.nlm.nih.gov/mesh/sparql",
                     "https://sparql.proconsortium.org/virtuoso/sparql", "https://sparql.rhea-db.org/sparql",
                     "http://patho.phenomebrowser.net/sparql/", "https://bio2rdf.org/sparql", "http://dbpedia.org/sparql"]

    list_query_graph = ["query/all_graphs_included.sparql", "query/graphs_with_a_triple_min.sparql",
                        "query/graphs_with_rdf_type.sparql"]

    list_query_endpoint = ["query/class.sparql", "query/property.sparql", "query/label_class.sparql",
                           "query/label_property.sparql", "query/property_domain_range.sparql", "query/subclass.sparql", 
                           "query/subproperty.sparql", "query/property_domain.sparql", "query/property_range.sparql",
                           "query/indi_range_property.sparql", "query/indi_domain_property.sparql",
                           "query/entity_type.sparql"]
    
    
    #repertoire data
    dir = "C:\data2"
    if os.path.exists(dir):
        shutil.rmtree(dir)

    os.makedirs("C:\data2")

    #repertoire endpoints
    for ep in list_endpoint:
        #repertoire endpoint
        endpoint_dir = os.path.join(dir,return_file_uri(ep))
        os.makedirs(endpoint_dir,exist_ok=True)
                
        compared_query = {}
        try:
            nb, q, res = launch_query(setting_query(list_query_graph[0], ep, None, 10000, True), None)
            if res != {}:
                compared_query[nb] = q, res
                # report - store the query and its results
                report_query_graph[q] = nb

            # getting graph query with most results and its list of graphs
            list_graph, more_result_query = extract_graph(compared_query, ep)
        except:
            print(f"Exception pour recuperation des graphes / endp : {ep}")
            list_graph = {}

        for graph in list_graph:
            print("Graph: " + graph)                        
            graph_dir = os.path.join(endpoint_dir,return_file_uri(graph))
            os.makedirs(graph_dir,exist_ok=True)

            try:
                # lancement de la requete pour recuperer les classes
                nb, q, res = launch_query(setting_query(list_query_endpoint[0], ep, graph, 100000, False), 1)

                # Ecriture du fichier classes 
                if res != {} and nb != 0:
                    data = []
                    print(f"-----------recuperation des classes : {nb}")
                    for r in res["results"]["bindings"]:
                        data.append({"class": r["class"]["value"]})

                    with open(graph_dir + "/classes.json", "w") as f:
                        json.dump(data, f, indent=2)
                    f.close()
            except:
                print("!!!!!!!!!!recuperation des classes : exception")


            try:
                # Lancement de la requete pour recuperer les proprietes
                nb2, q2, res2 = launch_query(setting_query(list_query_endpoint[1], ep, graph, 100000, False), 1)


                # Ecriture du fichier properties 
                if res2 != {} and nb2 != 0:
                    data = []
                    print(f"-----------recuperation des properties : {nb2}")
                    for r in res2["results"]["bindings"]:
                        data.append({"property": r["property"]["value"]})
                        
                    with open(graph_dir + "/properties.json", "w") as f:
                        json.dump(data, f, indent=2)
                    f.close()
            except:
                print("!!!!!!!!!!!recuperation des properties : exception")


            try:
                # Lancement de la requete pour recuperer les labels des classes
                nb3, q3, res3 = launch_query(setting_query(list_query_endpoint[2], ep, graph, 10000, False), 1)


                # Ecriture du fichier des labels des classes 
                if res3 != {} and nb3 != 0:
                    data = []
                    print(f"-----------recuperation des labels classes : {nb3}")
                    for r in res3["results"]["bindings"]:
                        data.append({"class": r["class"]["value"], "label": r["label"]["value"], "lang": r["lang"]["value"]})
                        
                    with open(graph_dir + "/labels_class.json", "w") as f:
                        json.dump(data, f, indent=2)
                    f.close()
            except:
                print("!!!!!!!!!recuperation des labels classes : exception")


            try:
                # Lancement de la requete pour recuperer les labels des proprietes
                nb4, q4, res4 = launch_query(setting_query(list_query_endpoint[3], ep, graph, 10000, False), 1)

                # Ecriture du fichier des labels des proprietes 
                if res4 != {} and nb4 != 0:
                    data = []
                    print(f"-----------recuperation des labels property : {nb4}")
                    for r in res4["results"]["bindings"]:
                        data.append({"property": r["property"]["value"], "label": r["label"]["value"], "lang": r["lang"]["value"]})
                        
                    with open(graph_dir + "/labels_property.json", "w") as f:
                        json.dump(data, f, indent=2)
                    f.close()
            except:
                print("!!!!!!!recuperation des labels property : exception")


            try:
                # Lancement de la requete pour recuperer les properties, domains et ranges
                nb5, q5, res5 = launch_query(setting_query(list_query_endpoint[4], ep, graph, 10000, False), 1)

                # Ecriture du fichier des properties, domains et ranges
                if res5 != {} and nb5 != 0:
                    data = []
                    print(f"-----------recuperation des property domain range : {nb5}")
                    for r in res5["results"]["bindings"]:
                        data.append({"domain": r["domain"]["value"], "property": r["property"]["value"], "range": r["range"]["value"]})
                    
                    with open(graph_dir + "/domains_properties_ranges.json", "w") as f:
                        json.dump(data, f, indent=2)
                    f.close()
            except:
                print("!!!!!!!!!recuperation des property domain range : exception")

            
            try:
                # Lancement de la requete pour recuperer les properties et domains
                nb6, q6, res6 = launch_query(setting_query(list_query_endpoint[7], ep, graph, 10000, False), 1)

                # Ecriture du fichier des properties et domains
                if res6 != {} and nb6 != 0:
                    data = []
                    with open (graph_dir + "/domains_properties_ranges.json", "r") as f:
                        dom_prop_ran = json.load(f)
                    f.close()

                    print(f"-----------recuperation des property domain : {nb6}")
                    for r in res6["results"]["bindings"]:
                        domain = r["domain"]["value"]
                        property = r["property"]["value"]

                        if not any(domain in item.values() and property in item.values() for item in dom_prop_ran):
                            data.append({"domain": domain, "property": property})
                    
                    with open(graph_dir + "/domains_properties.json", "a") as f:
                        json.dump(data, f, indent=2)
                    f.close()  
            except:
                print("!!!!!!!!!recuperation des property domain : exception")


            try:
                # Lancement de la requete pour recuperer les properties et range
                nb7, q7, res7 = launch_query(setting_query(list_query_endpoint[8], ep, graph, 10000, False), 1)

                # Ecriture du fichier des properties et ranges
                if res7 != {} and nb7 != 0:
                    data = []
                    with open (graph_dir + "/domains_properties_ranges.json", "r") as f:
                        dom_prop_ran = json.load(f)
                    f.close()
                    print(f"-----------recuperation des property property range : {nb7}")
                    for r in res7["results"]["bindings"]:
                        property = r["property"]["value"]
                        range = r["range"]["value"]
                        if not any(property in item.values() and range in item.values() for item in dom_prop_ran):
                            data.append({"property": property, "range": range})

                    
                    with open(graph_dir + "/properties_ranges.json", "a") as f:
                        json.dump(data, f, indent=2)
                    f.close()
            except:
                print(f"!!!!!!!!recuperation des property property range : exception")

                    
        print("---------------")


main()
