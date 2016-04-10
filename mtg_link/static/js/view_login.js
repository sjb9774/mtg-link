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

  var signUpPasswordInputs = $('#sign-up-password, #sign-up-password-confirm');
  signUpPasswordInputs.on('blur', function(evt) {
    if ($('#sign-up-password').val() !== $('#sign-up-password-confirm').val()) {
      $('.match-passwords-alert').show();
    } else {
      $('.match-passwords-alert').hide();
    }
  });

  var signUpSubmitButton = $('#sign-up-submit-button');
  signUpSubmitButton.on('click', function(evt) {
    var callback = function(resp) {
      if (resp.success) {
        redirect('/login');
      } else {
        alert("There was a problem signing up, please try again.");
      }

    };

    var username = $('#sign-up-username').val();
    var password = $('#sign-up-password').val();
    var confirmPassword = $('#sign-up-password-confirm').val();

    if (password === confirmPassword) {
      var payload = {
          'url': '/api/register',
          'data': {'username': username, 'password': password},
          'success': callback
      };
      $.post(payload);
    } else {
      alert("Your passwords still don't match!");
    }
  });
});
