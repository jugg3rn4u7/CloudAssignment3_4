$(document).ready(function () {

	$("input[name='sql_query']").change(function(){
	    var selected_option = $('input[name=sql_query]:radio:not(:checked)').val("1");
	    var isDisabled = $("#cache_query").is('[disabled=disabled]');

	    console.log("selected_option : ", selected_option);
		
		if(selected_option == "1") {

			if(isDisabled) {
				$("#cache_query").removeAttr( "disabled" );
			}

	    } else {

			if(!isDisabled) {
				$("#cache_query").attr( "disabled", "disabled" );
			}
	    }
	});

	var getData = function () {

		var selected_option = $('input[name=sql_query]:radio:not(:checked)').val();

		if(selected_option == "1") {

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

		} else {


			var url = '/insert_query?_ts=' + (new Date()).getTime();

		  	var callback = function (response) {
		  		if( response ) {
		  			console.log("Response: ");
		  			console.log(response);
		  			var time_elapsed = response.results.time_elapsed;
		  			$("#time_elapsed").html(time_elapsed + " milliseconds");
		  		} 
		  	};

		  	var dataType = 'JSON';
			var data = { query: $("#query").val(), times: $("#times").val() };
			$.ajax({
			  type: "POST",
			  url: url,
			  success: callback,
			  failure: callback,
			  dataType: dataType,
			  data: data
			});

		}
		
	}

	var getQueries = function () {

		var url = '/getQueries?_ts=' + (new Date()).getTime();

	  	var callback = function (response) {
	  		if( response ) {
	  			console.log("GET QUERIES Response: ");
	  			console.log(response);
	  			$("#list-of-queries").html("");
	  			var json_data = response;
	  			console.log(json_data);
	  			for (var i = 0; i < json_data.length; i++) {
	  			 	$("#list-of-queries").append('<tr><th scope="row">'+(i+1)+'</th><td>'+ json_data[i][1] +'</td><td><input type="text" value="1" style="width: 50%;"></input></td><td><button data-query="'+ (i+1) +'" class="btn btn-info" type="button" id="'+ json_data[i][0] +'">Get Cache</button></td></tr>');
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

		var url = '/cquery?_ts=' + (new Date()).getTime();

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
	$("#refresh-list").on("click", getQueries);

	$(document).delegate("[data-query]", "click", function(e) {
		var id = $(this).attr("id");
		var times = $( $(this).parent() ).parent().find("input").val();
		console.log("Cached Query params: ", id, times);
		runCachedQuery(id, times);
	});

	getQueries()
});
