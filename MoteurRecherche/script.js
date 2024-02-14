//gerer l'affichage de la recherche en fonction du formulaire
function submit() {
	let val = $('#valeur').val()
	$("#res").empty()
	$("#res_title").text(`Searching for "${val}"`);

	// Expressions régulières pour extraire les préfixes et les valeurs
	const classConst = /^class:(.*)$/;
	const propertyConst = /^property:(.*)$/;
	const domainConst = /^domain:(.*)$/;
	const rangeConst = /^range:(.*)$/;
	const resConst = /#results#/;


	// valeurs entrees
	let searchType = null;
	let searchName = null;
	let domain = null;
	let property = null;
	let range = null;

	let terms = val.split(' ')
	if (!terms) { terms.append(val)}
		
	// boucle pour chaque terme
	for (let i = 0; i < terms.length; i++) {
		term = terms[i]
		let isClass = classConst.exec(term);
		let isProperty = propertyConst.exec(term);
		let isDomain = domainConst.exec(term);
		let isRange = rangeConst.exec(term);
		let isRes = resConst.exec(term);
		
		// Dispatcher	
		if (isClass) {
			searchType = "class";
			searchName = isClass[1];

		} else if (isProperty) {
			searchType = "property";
			property = isProperty[1];
			searchName = isProperty[1];

		} else if (isDomain) {
			domain = isDomain[1];
			searchType = "class";
			searchName = isDomain[1];

		} else if (isRange) {
			range = isRange[1];
			searchType = "class";
			searchName = isRange[1];

		} else if(isRes) {
			searchType = "endpoint"
		} else {
			searchName = term;
		}
	}
	
	// recheche des domains, properties ou ranges a partir d'un doublet
	if ((domain && range && !property) || (domain && property && !range) || (property && range && !domain)) {
		search_dom_ran(domain, property, range)
	
	// rechercher des doublet à partir d'un domain, property ou range
	} else if ((domain && !property && !range) || (!domain && !property && range)) {
		search_dom_prop_ran_prop(domain, range);

	// recherche simple sur un nom/label
	} else if (searchName) {
		search_entity(searchName, searchType);

	//recherche de touts les endpoints geres par le moteur de recherche
	} else if (searchType == "endpoint") {
		search_endpoints();
	} else {
		console.log('recherche non gerer');
	}

}

// recuperer tous les endpoints
function search_endpoints() {

	$.ajax({
		url: "http://localhost:9200/entities/_search?size=0",
		method: "POST",
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify({
			"aggs": {
			  "unique_endpoints": {
				"terms": {
				  "field": "endpoint",
				  "size": 100000
				}
			  }
			}
		}),
		success: function(data) {	
			var endpoints = data.aggregations.unique_endpoints.buckets;
			var title = "Total d'endpoint : " + endpoints.length

			$("#res").empty()
			$("#res_title").text(title);
			
			var tab = document.createElement('table');
			var ligne = document.createElement('tr');
			var cellule = document.createElement('td');
			cellule.innerHTML = "Endpoint URI";
			ligne.appendChild(cellule);
			tab.appendChild(ligne)
			endpoints.forEach(function(endpoint) {
				var edp = endpoint.key;
				ligne = document.createElement('tr');
				cellule = document.createElement('td');
				cellule.innerHTML = edp
				cellule.addEventListener("click", function() {
					search_graphs(edp);
				})
				ligne.appendChild(cellule)
				tab.appendChild(ligne)
			});
			$("#res").append(tab)
		},
		error: function() {
			// Gérer les erreurs
			console.log("erreur acces au serveur elasticsearch");
		}
	});


}

// recuperer tous les graphes d'un endpoint
function search_graphs(endpoint) {

	$.ajax({
		url: "http://localhost:9200/entities/_search?size=0",
		method: "POST",
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify({
			"query": {
				"term": {
					"endpoint": endpoint
				}
			},
			"aggs": {
				"unique_graphs": {
					"terms": {
						"field": "graph",
						"size": 100000
					}
				}
			}
		}),
		success: function(data) {	
			var graphs = data.aggregations.unique_graphs.buckets;
			var title = "Total de graphe de l'endpoint \"" + endpoint + "\" : " + graphs.length
			$("#res").empty()
			$("#res_title").text(title);
			
			var tab = document.createElement('table');
			var ligne = document.createElement('tr');
			var cellule = document.createElement('td');
			cellule.innerHTML = "Graph URI";
			ligne.appendChild(cellule);
			tab.appendChild(ligne)
			graphs.forEach(function(graph) {
				var g = graph.key;
				ligne = document.createElement('tr');
				cellule = document.createElement('td');
				cellule.innerHTML = g
				cellule.addEventListener("click", function() {
					search_entities(g);
				})
				ligne.appendChild(cellule)
				tab.appendChild(ligne)
			});
			$("#res").append(tab)
		},
		error: function() {
			// Gérer les erreurs
			console.log("erreur acces au serveur elasticsearch");
		}
	});

}

// recuperer toutes les entites d'un graphe
function search_entities(graph) {

	$.ajax({
		url: "http://localhost:9200/entities/_search?size=10000",
		method: "POST",
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify({
			"query": {
				"term": {
					"graph": graph
				}
			}
		}),
		success: function(data) {	
			var title = "Total d'entite dans le graph \"" + graph + "\" : " + data['hits']['total']['value']
			$("#res").empty()
			$("#res_title").text(title);
			
			var tab = document.createElement('table');
			var ligne = document.createElement('tr');
			var cellule = document.createElement('td');
			cellule.innerHTML = "URI";
			ligne.appendChild(cellule);
			tab.appendChild(ligne)
			data['hits']['hits'].forEach(e => {
				var uri = e['_source']['uri']
				console.log(uri)
				ligne = document.createElement('tr');
				cellule = document.createElement('td');
				cellule.innerHTML = uri
				ligne.appendChild(cellule)
				tab.appendChild(ligne)
			});
			$("#res").append(tab)
		},
		error: function() {
			// Gérer les erreurs
			console.log("erreur acces au serveur elasticsearch");
		}
	});

}



//mettre à jour la barre de recherche
function update_search(val, type) {
	console.log(val + " : " + type)
	console.log($('#valeur').val())
	v = (type == "domain" || type == "range" || type == "class") ? ("class:"+val) : ("property:"+val);
	$('#valeur').val(v)
	submit();
}

// rechercher domain-property ou property-range
function search_dom_prop_ran_prop(domain, range) {
	let param;

	if (domain) {
		param = domain;

	} else if (range) {
		param = range;

	}

	query = {
		"query": {
			"bool": {
				"must": [
					{
					"match": {
						"entityType": "class"
						}
					},
					{
					"match": {
						"name": param
						}
					}
				]
			}
		}
	}

	$.ajax({
		url: "http://localhost:9200/entities/_search?size=10000",
		method: "POST",
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify(query),
		success: function(data) {	
			$("#res").empty()
			var nb = 0;
			var tab = document.createElement('table');
			var ligne = document.createElement('tr');
			var cellule = document.createElement('td');
			cellule.innerHTML = "domain";
			ligne.appendChild(cellule);
			cellule = document.createElement('td');
			cellule.innerHTML = "property";
			ligne.appendChild(cellule);
			cellule = document.createElement('td');
			cellule.innerHTML = "range";
			ligne.appendChild(cellule);
			cellule = document.createElement('td');
			cellule.innerHTML = "graph";
			ligne.appendChild(cellule);
			cellule = document.createElement('td');
			cellule.innerHTML = "endpoint";
			ligne.appendChild(cellule);
			tab.appendChild(ligne);

			data["hits"]["hits"].forEach(prop => {
				let graph = prop["_source"]["graph"];
				let endpoint = prop["_source"]["endpoint"]
				let uri = prop["_source"]["uri"];

				if (domain) {
					prop["_source"]["isDomainOf"].forEach(e => {
						nb += 1;
						let prop = e["propertyName"];
						let p = prop
						let ran = (e["rangeName"]) ? e["rangeName"] : "unknown";
						let r = ran

						// ajout a la liste
						ligne = document.createElement('tr');
						cellule = document.createElement("td");
						span = document.createElement('strong');
						span.innerHTML = `${domain}`;
						span.addEventListener("click",function() {
							update_search(domain, "class")
						});	
						cellule.append(span);
						//logo
						let logo = document.createElement('img')
						logo.src = "img/logo_lien_externe.png";
						logo.width = 15;
						logo.height = 20;
						let lien = document.createElement('a');
						lien.href = uri;;
						lien.title = uri;
						lien.appendChild(logo)
						cellule.append(lien);					
						ligne.appendChild(cellule);

						cellule = document.createElement('td');
						span = document.createElement('span');
						span.innerHTML = `${prop}`;
						span.addEventListener("click",function() {
							update_search(p, "property")
						});	
						cellule.append(span);
						//logo
						logo = document.createElement('img')
						logo.src = "img/logo_lien_externe.png";
						logo.width = 15;
						logo.height = 20;
						lien = document.createElement('a');
						lien.href = e["propertyUri"];;
						lien.title = e["propertyUri"];;
						lien.appendChild(logo)
						cellule.append(lien);					
						ligne.appendChild(cellule);
						cellule = document.createElement('td');
						span = document.createElement('span');
						span.innerHTML = `${ran}`;
						span.addEventListener("click",function() {
							update_search(r, "range")
						});
						cellule.append(span)
						//logo
						logo = document.createElement('img')
						logo.src = "img/logo_lien_externe.png";
						logo.width = 15;
						logo.height = 20;
						lien = document.createElement('a');
						lien.href = e["rangeUri"];;
						lien.title = e["rangeUri"];;
						lien.appendChild(logo)
						cellule.append(lien);	
						ligne.appendChild(cellule);
						cellule = document.createElement('td');
						cellule.innerHTML = `<span>${graph}</span>`;
						ligne.appendChild(cellule);
						cellule = document.createElement('td');
						cellule.innerHTML = `<span>${endpoint}</span>`;
						ligne.appendChild(cellule);
						tab.appendChild(ligne);
					});
				} else if (range) {
					prop["_source"]["isRangeOf"].forEach(e => {
						nb += 1;
						let dom = (e["domainName"]) ? e["domainName"] : "unknown";
						let d = dom
						let prop = e["propertyName"];
						let p = prop
						// ajout a la liste
						ligne = document.createElement("tr");
						cellule = document.createElement('td');
						span = document.createElement('span');
						span.innerHTML = `${dom}`;
						span.addEventListener("click",function() {
							update_search(d, "domain")
						});
						cellule.append(span)
						//logo
						let logo = document.createElement('img')
						logo.src = "img/logo_lien_externe.png";
						logo.width = 15;
						logo.height = 20;
						let lien = document.createElement('a');
						lien.href = e["domainUri"];;
						lien.title = e["domainUri"];;
						lien.appendChild(logo)
						cellule.append(lien);	
						ligne.appendChild(cellule)
						cellule = document.createElement('td');
						span = document.createElement('span');
						span.innerHTML = `${prop}`;
						span.addEventListener("click",function() {
							update_search(p, "property")
						});
						cellule.append(span)
						//logo
						logo = document.createElement('img')
						logo.src = "img/logo_lien_externe.png";
						logo.width = 15;
						logo.height = 20;
						lien = document.createElement('a');
						lien.href = e["propertyUri"];;
						lien.title = e["propertyUri"];;
						lien.appendChild(logo)
						cellule.append(lien);	
						ligne.appendChild(cellule);
						cellule = document.createElement("td");
						span = document.createElement('strong');
						span.innerHTML = `${range}`;
						span.addEventListener("click",function() {
							update_search(range, "class")
						});	
						cellule.append(span);
						//logo
						logo = document.createElement('img')
						logo.src = "img/logo_lien_externe.png";
						logo.width = 15;
						logo.height = 20;
						lien = document.createElement('a');
						lien.href = uri;;
						lien.title = uri;
						lien.appendChild(logo)
						cellule.append(lien);					
						ligne.appendChild(cellule);
						cellule = document.createElement('td');
						cellule.innerHTML = `<span>${graph}</span>`;
						ligne.appendChild(cellule);
						cellule = document.createElement('td');
						cellule.innerHTML = `<span>${endpoint}</span>`;
						ligne.appendChild(cellule);
						tab.appendChild(ligne);
					});
				}							
			});
			let title = document.createElement('h2');
			title.innerHTML = (nb > 1) ? nb + " Properties :" : nb + " Property :"
			$('#res').append(title)
			$("#res").append(tab)		
		},
		error: function() {
			// Gérer les erreurs
			console.log("erreur acces au serveur elasticsearch");
		}
	});

}

// rechercher domain ou range ou property
function search_dom_ran(domain, property, range) {

	let param1;
	let param2;
	let search;
	let query;
	if (!range) {
		param1 = domain;
		param2 = property;
		search = "range";
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
	} else if (!domain) {
		param1 = property;
		param2 = range;
		search = "domain";
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
	} else if (!property) {
		param1 = domain;
		param2 = range;
		search = "property";
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
	}

	$.ajax({
		url: "http://localhost:9200/entities/_search?size=10000",
		method: "POST",
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify(query),
		success: function(data) {	
			$("#res").empty()
			var nb = 0;
			var tab = document.createElement('table');
			var ligne = document.createElement('tr');
			var cellule = document.createElement('th');
			cellule.innerHTML = search;
			ligne.appendChild(cellule);
			cellule = document.createElement('th');
			cellule.innerHTML = `graph`;
			ligne.appendChild(cellule);
			cellule = document.createElement('th');
			cellule.innerHTML = `endpoint`;
			ligne.appendChild(cellule);
			tab.appendChild(ligne);

			data["hits"]["hits"].forEach(prop => {
				nb += 1;
				graph = prop["_source"]["graph"]
				endpoint = prop["_source"]["endpoint"]
				uri = prop["_source"]["uri"]
				nom = prop["_source"]["name"]
				
				// ajout a la liste
				var ligne = document.createElement("tr");
				var cellule = document.createElement('td');
				cellule.innerHTML = `<span>${nom}</span>`;
				cellule.addEventListener("click",function() {
					if (!property) {
						update_search(nom, "property")
					} else {
						update_search(nom, "class")
					}
				});
				//logo
				let logo = document.createElement('img')
				logo.src = "img/logo_lien_externe.png";
				logo.width = 15;
				logo.height = 20;
				let lien = document.createElement('a');
				lien.href = uri;
				lien.title = uri;
				lien.appendChild(logo)
				cellule.append(lien);	
				ligne.appendChild(cellule);
				cellule = document.createElement('td');
				cellule.innerHTML = `<span>${graph}</span>`;
				ligne.appendChild(cellule);
				cellule = document.createElement('td');
				cellule.innerHTML = `<span>${endpoint}</span>`;
				ligne.appendChild(cellule);
				tab.appendChild(ligne);
			});
			let title = document.createElement('h2');
			title.innerHTML = (nb > 1) ? nb + " Properties (" + search +") :" : nb + " Property (" + search + "):"
			$('#res').append(title)
			$("#res").append(tab)	
			
			
		},
		error: function() {
			// Gérer les erreurs
			console.log("erreur acces au serveur elasticsearch")
		}
	});
}



function create_res(typ, data) {
	var src = document.createElement('div');
	res_OK = false;
	nb = 0;


	data["hits"]["hits"].forEach(prop => {

		var type = prop["_source"]["entityType"];
		var uri = prop["_source"]["uri"];
		var name = prop["_source"]["name"];
		var graph = prop["_source"]["graph"];
		var endpoint = prop["_source"]["endpoint"];
		var isDomainOf = prop["_source"]["isDomainOf"];
		var isPropertyOf = prop["_source"]["isPropertyOf"];
		var isRangeOf = prop["_source"]["isRangeOf"];

		if(type == typ) {
			nb += 1;
			res_OK = true
			var tab = document.createElement('table');

			let ligne = document.createElement('tr');
			let cellule = document.createElement('th');
			cellule.innerHTML = (type == "class") ? "class" : "property";
			ligne.appendChild(cellule);
			cellule = document.createElement('td');
			cellule.innerHTML = `<span>${name}</span>`
			ligne.appendChild(cellule)
			tab.appendChild(ligne);


			ligne = document.createElement('tr');
			cellule = document.createElement('th');
			cellule.innerHTML = "URI";
			ligne.appendChild(cellule);
			cellule = document.createElement('td');
			cellule.innerHTML = `<span>${uri}</span>`
			//logo
			let logo = document.createElement('img')
			logo.src = "img/logo_lien_externe.png";
			logo.width = 15;
			logo.height = 20;
			let lien = document.createElement('a');
			lien.href = uri;
			lien.title = uri;
			lien.appendChild(logo)
			cellule.append(lien);
			ligne.appendChild(cellule)
			tab.appendChild(ligne);

			ligne = document.createElement('tr');
			cellule = document.createElement('th');
			cellule.innerHTML = "graph";
			ligne.appendChild(cellule);
			cellule = document.createElement('td');
			cellule.innerHTML = `<span>${graph}</span>`
			ligne.appendChild(cellule)
			tab.appendChild(ligne);

			ligne = document.createElement('tr');
			cellule = document.createElement('th');
			cellule.innerHTML = "endpoint";
			ligne.appendChild(cellule);
			cellule = document.createElement('td');
			cellule.innerHTML = `<span>${endpoint}</span>`
			ligne.appendChild(cellule)
			tab.appendChild(ligne);


			if (type == "class") {
				ligne = document.createElement('tr');
				cellule = document.createElement('th');
				cellule.innerHTML = "domain-of";
				ligne.appendChild(cellule);
				cellule = document.createElement('td');
				if (isDomainOf.length != 0) {
					var listDom = document.createElement('ol');
					isDomainOf.forEach(i => {
						el = document.createElement('li');
						if (i["propertyName"]) {
							span = document.createElement('span');
							span.innerHTML = `property : ${i["propertyName"]}  `;
							span.addEventListener("click",function() {
								update_search(i["propertyName"], "property")
							});
							el.append(span);
							//logo
							let logo = document.createElement('img')
							logo.src = "img/logo_lien_externe.png";
							logo.width = 15;
							logo.height = 20;
							let lien = document.createElement('a');
							lien.href = i["propertyUri"];
							lien.title = i["propertyUri"];
							lien.appendChild(logo)

							el.append(lien);
						}
						if (i["rangeName"]) {
							span = document.createElement('span');
							span.innerHTML = `&nbsp;&nbsp;&nbsp;range : ${i["rangeName"]} `;
							span.addEventListener("click",function() {
								update_search(i["rangeName"], "range")
							});
							el.append(span);
							//logo
							let logo = document.createElement('img')
							logo.src = "img/logo_lien_externe.png";
							logo.width = 15;
							logo.height = 20;
							let lien = document.createElement('a');
							lien.href = i["rangeUri"];
							lien.title = i["rangeUri"];
							lien.appendChild(logo)

							el.append(lien);
						}
						listDom.appendChild(el);

					})
					var $listDom = $(listDom);
					$listDom.hide();
					var buttonDom = document.createElement('button')
					buttonDom.innerHTML = 'Afficher'
					buttonDom.addEventListener("click", function() {
						$listDom.toggle()
						buttonDom.innerHTML = (buttonDom.innerHTML == 'Afficher') ? 'Masquer' : 'Afficher';
						}
					);
					cellule.append(buttonDom,listDom);
				} else {
					el = document.createElement('span');
					el.innerHTML = "Pas de resultat"
					cellule.append(el);
				}
				ligne.appendChild(cellule)
				tab.appendChild(ligne);
				


				ligne = document.createElement('tr');
				cellule = document.createElement('th');
				cellule.innerHTML = "range-of";
				ligne.appendChild(cellule);
				cellule = document.createElement('td');
				if (isRangeOf.length != 0) {
					var listRan = document.createElement('ol');					
					isRangeOf.forEach(i => {
						el = document.createElement('li');
						if (i["domainName"]) {
							span = document.createElement('span');
							span.innerHTML = `domain : ${i["domainName"]} `;
							span.addEventListener("click",function() {
								update_search(i["domainName"], "domain")
							});
							el.append(span)
							//logo
							let logo = document.createElement('img')
							logo.src = "img/logo_lien_externe.png";
							logo.width = 15;
							logo.height = 20;
							let lien = document.createElement('a');
							lien.href = i["domainUri"];
							lien.title = i["domainUri"];
							lien.appendChild(logo)

							el.append(lien);
						}
						if (i["propertyName"]) {						
							span = document.createElement('span');
							span.innerHTML = `&nbsp;&nbsp;&nbsp;property : ${i["propertyName"]} `;
							span.addEventListener("click",function() {
								update_search(i["propertyName"], "property")
							});
							el.append(span)
							//logo
							let logo = document.createElement('img')
							logo.src = "img/logo_lien_externe.png";
							logo.width = 15;
							logo.height = 20;
							let lien = document.createElement('a');
							lien.href = i["propertyUri"];
							lien.title = i["propertyUri"];
							lien.appendChild(logo)

							el.append(lien);
						}
						listRan.appendChild(el);

					})
					var $listRan = $(listRan);
					$listRan.hide();
					var buttonRan = document.createElement('button')
					buttonRan.innerHTML = 'Afficher'
					buttonRan.addEventListener("click", function() {
						$listRan.toggle()
						buttonRan.innerHTML = (buttonRan.innerHTML == 'Afficher') ? 'Masquer' : 'Afficher';
						}
					);
					cellule.append(buttonRan, listRan)
				} else {
					el = document.createElement('span');
					el.innerHTML = "Pas de resultat"
					cellule.append(el);
				}
				ligne.appendChild(cellule)
				tab.appendChild(ligne);
			}


			if (type == "property") {
				ligne = document.createElement('tr');
				cellule = document.createElement('th');
				cellule.innerHTML = "property-of";
				ligne.appendChild(cellule);
				cellule = document.createElement('td');
				if (isPropertyOf.length != 0) {
					var listProp = document.createElement('ol');
					isPropertyOf.forEach(i => {
						el = document.createElement('li');
						if (i["domainName"]) {
							span = document.createElement('span');
							span.innerHTML = `domain : ${i["domainName"]} `;
							span.addEventListener("click", function() {
								update_search(i["domainName"], "domain")
							});
							el.append(span);
							//logo
							let logo = document.createElement('img')
							logo.src = "img/logo_lien_externe.png";
							logo.width = 15;
							logo.height = 20;
							let lien = document.createElement('a');
							lien.href = i["domainUri"];
							lien.title = i["domainUri"];
							lien.appendChild(logo)

							el.append(lien);
						}
						if (i["rangeName"]) {
							span = document.createElement('span');
							span.innerHTML = `&nbsp;&nbsp;&nbsp;range : ${i["rangeName"]} `;
							span.addEventListener("click", function() {
								update_search(i["rangeName"], "range")
							});
							el.append(span);
							//logo
							let logo = document.createElement('img')
							logo.src = "img/logo_lien_externe.png";
							logo.width = 15;
							logo.height = 20;
							let lien = document.createElement('a');
							lien.href = i["rangeUri"];
							lien.title = i["rangeUri"];
							lien.appendChild(logo)

							el.append(lien);
						}
						listProp.appendChild(el);

					})
					var $listProp = $(listProp);
					$listProp.hide();
					var buttonProp = document.createElement('button')
					buttonProp.innerHTML = 'Afficher'
					buttonProp.addEventListener("click", function() {
						$listProp.toggle()
						buttonProp.innerHTML = (buttonProp.innerHTML == 'Afficher') ? 'Masquer' : 'Afficher';

						}
					);
					cellule.append(buttonProp, listProp)
				} else {
					el = document.createElement('span');
					el.innerHTML = "Pas de resultat"
					cellule.appendChild(el);
				}
				ligne.appendChild(cellule)
				tab.appendChild(ligne);

			}
			
			src.append(tab)
		}
	});

	if (!res_OK) {
		err = document.createElement('h2');
		err.innerHTML = "Aucun resultat";
		return [0,err];
	} else {
		return [nb, src];
	}

}

// rechercher classe /propriete
function search_entity(val, type) {
	
	query = {
		"query": {
			"bool": {
				"must": [
					{
					"bool": {
						"should": [ 
							{
							"match": {
								"name": val
							}
							},
							{
							"nested": {
								"path": "labels",
								"query": {
									"bool": {
										"must": [
											{
												"term": {
													"labels.label": {
														"value": val
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
				]
			}
        }
	}

	if (type != null) {
		query["query"]["bool"]["must"].push({
            "match": {
                "entityType": type
            }
        })
	}


	$.ajax({
		url: "http://localhost:9200/entities/_search?size=10000",
		method: "POST",
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify(query),
		success: function(data) {	
			
			// Traiter les résultats et mettre à jour l'interface utilisateur
			let title = "Results :  ";
			let tabClass = null;
			let tabProperty = null;
			if (type == "class" || !type) {
				[nbc, tabClass] = create_res("class", data);
				title += (nbc > 1) ? `${nbc} Classes ` : `${nbc} Class `;
				title += (type == "property" || !type) ? "/ " : ":";
			}

			if (type == "property" || !type) {
				[nbp,tabProperty] = create_res("property", data);
				title += (nbp > 1) ? `${nbp} Properties :` : `${nbp} Property :`;
			}
			let res_title = document.createElement('h2');
			res_title.innerHTML = title;
			$('#res').append(res_title)
			if (tabClass) { 
				let type_title = document.createElement('h3')
				type_title.innerHTML = 'Classes :';
				res.appendChild(type_title);
				$('#res').append(tabClass) 
			}
			if (tabProperty) { 
				let type_title = document.createElement('h3')
				type_title.innerHTML = 'Properties :';
				res.appendChild(type_title);
				$('#res').append(tabProperty) 
		}

			
		},
		error: function() {
			// Gérer les erreurs
			console.log("erreur acces au serveur elasticsearch")
		}
	});
}


$(document).ready(function(){
	$('#search1').click(submit);
});

