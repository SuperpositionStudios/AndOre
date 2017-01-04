Vue.component('player', {
  template: '<li>This is a todo</li>'
});

var navbar = new Vue({
	delimiters: ['[[', ']]'],
	el: '#navbar',
	data: {
		message: 'Not Ready Yet'
	}
});
