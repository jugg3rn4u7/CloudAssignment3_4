$(document).ready(function () {

	var getData = function () {

		var url = '/query?_ts=' + (new Date()).getTime();

	  	var callback = function (response) {
	  		if( response ) {
	  			console.log("Response: ");
	  			console.log(response);
	  		} 
	  	};

	  	var dataType = 'JSON';
		var data = { query: $("#full_query").text(), times: $("#times").val() };
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
