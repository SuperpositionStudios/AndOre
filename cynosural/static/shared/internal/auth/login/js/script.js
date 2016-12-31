function setAID(aid) {
	localStorage.setItem('aid', aid)
}

function getURLs(callback) {
	$.getJSON('/urls',
		function (data) {
			console.log("Cynosural: ", "URLs: ", data);
			callback(data);
		}
	);
}

function redirectToHomePage() {
	window.location.replace('/');
}

function hasAnAidValue() {
	aid = localStorage.getItem('aid') || null;
	return null != aid;
}

function startSubmitButtonListener(erebusURL) {
	console.log("Starting to listen to the submit button");
	$('#submit').click(function () {
		var username = $('#username').val();
		var password = $('#password').val();
		var data = {
			username: username,
			password: password
		};

		$.ajax({
			method: 'POST',
			url: erebusURL + '/account/login',
			data: JSON.stringify(data),
			dataType: "json",
			contentType: "application/json",
			success: function (data) {
				if (data['status'] == 'Success') {
					Materialize.toast("Logged in", 2000, 'rounded light-green accent-4');
					setAID(data['uid']);
					redirectToHomePage();
				} else {
					console.log(data);
				}
			},
			error: function (jqXHR, exception) {
				if (jqXHR.status === 401) {
					Materialize.toast('Invalid Username And/Or[e] Password', 3000, 'rounded red accent-4');
				} else {
					Materialize.toast('So something bad happened, but I don\'t exactly know what happened.', 3000, 'rounded red accent-4');
					console.log('Unknown Error. \n ' + jqXHR.responseText);
				}
			}
		});
	});
}

$(document).ready(function () {
	/*
	The Flow of the Script
	1. If the client has an aid value in local storage, redirect to the home page (if it's invalid it's not my problem)
	2. Get the address to Erebus from the server that served this page
	3. Start a listener for when the submit button is clicked
	4. When the submit button is clicked, go ahead and send a ajax request to erebus. If we get back an aid, set it
	in the local storage and redirect to the home page.
	 */
	if (hasAnAidValue()) {
		redirectToHomePage();
	}
	var urls = null;
	getURLs(function (data) {
		urls = data;
		if (urls == null) {
			alert("And/Ore is currently down :(")
		}
		startSubmitButtonListener(urls.erebus);
	});
});