$(document).ready(function () {

	var getFiles = function () {

		var url = '/files';
	  	var callback = function (response) {
	  		if( response ) {
	  			console.log("List of files: ");
	  			console.log(response);
	  			var data = response["results"];
	  			console.log("data", data);
	  			$("#total_size").html("");
	  			$("#total_size").html(data["total"]);
	  			$("#list-of-files").html("")
	  			for (var i = 0; i < data["files"].length; i++) {
	  				$("#list-of-files").append('<tr><th scope="row">'+(i+1)+'</th><td><a href="/download/'+ data["ids"][i] +'">'+(data["files"][i]).split(/_(.+)?/)[1]+'</a></td><td>'+ data["sizes"][i] +'</td><td><button data-delete="'+ (i+1) +'" class="btn btn-danger" type="button" id="'+ data["files"][i] +'">Delete</button></td></tr>');
	  				$("#files").append('<option class="file-selector" data-option='+ data["ids"][i] +' value="'+ (data["files"][i]).split(/_(.+)?/)[1] +'">');
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

	$("#refresh-list").on("click", getFiles);

	var deleteFile = function (filename) {
		var url = '/delete/'+filename;
		$.ajax({
		  type: "GET",
		  url: url
		});
	}

	$(document).delegate("[data-delete]", "click", function(e) {
		var id = $(this).attr("id");
		deleteFile(id);
	});

	$(document).delegate("#login", "click", function(e) {
		var url = "/authenticate/username/" + $("#username").val() + "/password/" + $("#password").val();
		var dataType = 'JSON';
		$.ajax({
		  type: "GET",
		  url: url,
		  success: function (response) {
		  	$("#login-popup").removeClass("show").addClass("hide");
			setCookie(1);
		  },
		  failure: function (response) {
		  	console.log("Invalid login");
		  },
		  dataType: dataType
		});
	});

	var getPassword = function (user) {
		var url = '/getPassword/'+user;
		$.ajax({
		  type: "GET",
		  url: url,
		  success: function (response) {
		  	var password = response["results"]["password"]
		  	$("#user-password").val(password);
		  }
		});
	}

	$(document).delegate("#get-password", "click", function(e) {
		var user = $("#user").val();
		getPassword(user);
	});

	$(document).delegate(".file-selector", "click", function(e) {
		var file_id = $(this).data("option");
	});

	var searchFile = function (file_id) {
		var url = '/getPassword/'+user;
		$.ajax({
		  type: "GET",
		  url: url,
		  success: function (response) {
		  	$("#user-password").text(response["results"]);
		  }
		});
	}

	var setCookie = function (logged) {
		document.cookie = "loggedIN=" + logged;
	}

	var checkCookie = function () {
		var cookie = document.cookie;
		var logged = cookie.split("=")[1];
		if(logged == "1") return true;
		else return false;
	}

	var checkLogin = function () {
		if(checkCookie()) return;
		else {
			$("#login-popup").removeClass("hide").addClass("show");
		}
	}

	// on page load
	getFiles();
	checkLogin();

});