var login = function() {
  var username = $('#usernameInput').val();
  var password = $('#passwordInput').val();
  var callback = function(resp) {
    if (resp.success) {
      Cookies.set('sessionId', resp.session_id)
      redirect('/account/' + username);
    } else {
      Cookies.set('sessionId', null);
      alert('There was a problem logging in');
    }
  };
  $.post({'url': '/api/login',
          'data':{'username': username, 'password': password},
          'success': callback});
}

$(document).on('ready', function onReady(evt) {
  var loginForm = $('.login-form-container');
  var loginButton = $('.login-button');
  loginForm.on('keydown', function(evt) {
    if (evt.keyCode == 13) {
      login();
    }
  });
  loginButton.on('click', function(evt) {
    login();
  });
});
