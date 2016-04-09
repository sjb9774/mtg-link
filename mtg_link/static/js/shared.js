var redirect = function(url) {
  window.location.href = url;
}

$(document).on('ready', function(evt) {
  var logoutButton = $('#logout-button');
  logoutButton.on('click', function(evt) {
    if (Cookies.get('sessionId')) {
      var callback = function(resp) {
        if (resp.success) {
          Cookies.set('sessionId', null);
          redirect('/login');
        } else {
          alert('Problem logging out!');
        }
      };

      var payload = {
        'url': '/api/logout',
        'data': {'sessionId': Cookies.get('sessionId')},
        'success': callback
      };
      $.post(payload);
    }
  });
});
