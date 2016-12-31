$(document).ready(function() {
	$('.button-collapse').sideNav();
	$('.dropdown-button').dropdown();
	populateAccountDropDownMenu();
	getURLs(populateNavbarWithPrivilegeSpecificButtons);
});

function populateAccountDropDownMenu() {
	if (hasAnAidValue()) {
		addLogOutButton();
	} else {
		addLoginButton();
		addRegisterButton();
	}
}

function populateNavbarWithPrivilegeSpecificButtons(urls) {
	if (hasAnAidValue()) {
		$.ajax({
			method: 'GET',
			url: urls.erebus + '/users/' + getAid('aid_here') + '/privileges',
			//dataType: "json",
			contentType: "application/json",
			success: function (data) {
				console.log("Cynosural: Privileges: ", data);

				if (data.privileges.Cynosural.canViewProductionDetails || false) {
					$('#navbar-production-overview').removeClass('invisible');
				}

				if (data.privileges.Cynosural.canViewSphere || false) {
					$('#navbar-sphere').removeClass('invisible');
				}
			},
			error: function (jqXHR, exception) {
				console.log('Invalid aid');
			}
		});
	}
}

function addLogOutButton() {
	$('#dropdown1').append('<li><a href="/auth/logout">Logout</a>');
}

function addLoginButton() {
	$('#dropdown1').append('<li><a href="/auth/login">Login</a>');
}

function addRegisterButton() {
	$('#dropdown1').append('<li><a href="/auth/register">Register</a>');
}

function getURLs(callback) {
	$.getJSON('/urls',
		function (data) {
			console.log("Cynosural: ", "URLs: ", data);
			callback(data);
		}
	);
}


function hasAnAidValue() {
	aid = localStorage.getItem('aid') || null;
	return null != aid;
}

function getAid(default_value) {
	return localStorage.getItem('aid') || default_value;
}