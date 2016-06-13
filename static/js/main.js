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

	$("#run_query").on("click", getData);
});
