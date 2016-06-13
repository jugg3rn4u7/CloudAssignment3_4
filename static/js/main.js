$(document).ready(function () {

	var getData = function () {

		var url = '/query?_ts=' + (new Date()).getTime();

	  	var callback = function (response) {
	  		if( response ) {
	  			console.log("Response: ");
	  			console.log(response);
	  			var time_elapsed = response.results.time_elapsed;
	  			$("#time_elapsed").html(time_elapsed + " milliseconds");
	  		} 
	  	};

	  	var dataType = 'JSON';
		var data = { query: $("#query").val(), times: $("#times").val(), cached: $("#cache_query").is(":checked") };
		$.ajax({
		  type: "POST",
		  url: url,
		  success: callback,
		  failure: callback,
		  dataType: dataType,
		  data: data
		});
	}

	var getQueries = function () {

		var url = '/getQueries?_ts=' + (new Date()).getTime();

	  	var callback = function (response) {
	  		if( response ) {
	  			console.log("Response: ");
	  			console.log(response);
	  			$("#list-of-queries").append("");
	  			var queries = response.results;
	  			for (var i = 0; i < queries.length; i++) {
	  			 	$("#list-of-queries").append('<tr><th scope="row">'+(i+1)+'</th><td>'+ queries[i][1] +'</td><td><input type="text" value=""></input></td><td><button data-query="'+ (i+1) +'" class="btn btn-info" type="button" id="'+ queries[i][0] +'">Run Query</button></td></tr>');
	  			}
	  		} 
	  	};

	  	var dataType = 'JSON';
		$.ajax({
		  type: "GET",
		  url: url,
		  success: callback,
		  failure: callback,
		  dataType: dataType
		});
	}

	var runCachedQuery = function (id, times) {

		var url = '/query?_ts=' + (new Date()).getTime();

	  	var callback = function (response) {
	  		if( response ) {
	  			console.log("Response: ");
	  			console.log(response);
	  			var time_elapsed = response.results.time_elapsed;
	  			$("#time_elapsed").html(time_elapsed + " milliseconds");
	  		} 
	  	};

	  	var dataType = 'JSON';
		var data = { id: id, times: times };
		$.ajax({
		  type: "POST",
		  url: url,
		  success: callback,
		  failure: callback,
		  dataType: dataType,
		  data: data
		});
	}

	$("#run_query").on("click", getData);
	$("#refresh-list").on("click", getData);

	$(document).delegate("[data-query]", "click", function(e) {
		var id = $(this).attr("id");
		var times = $( $(this).parent() ).find("input").val();
		runCachedQuery(id, times);
	});

	getQueries()
});
