var search = function(text, callback) {
  var onSuccess = function(resp) {
    if (callback) {
      callback(resp);
    }
  }
  $.get({'url': '/search?name=' + text, 'success': onSuccess});
}

var redirect = function(url) {
  window.location.href = url;
}

$(document).on('ready', function onReady(evt) {
  var searchButton = $('#navbar-search-button');
  var searchInput = $('#search-input');
  searchInput.on('keydown', function keyDown(evt) {
    if (evt.keyCode == 13) {
      var searchText = $('#search-input').val();
      search(searchText, function partial(resp) { redirect(resp.url); });
    }
  });
  searchButton.on('click', function(evt) {
    var searchText = $('#search-input').val();
    var onSuccess = function(evt) {
      if (evt.url) {
        search(searchText, function partial(resp) { redirect(resp.url); });
      }
    }
    $.get({'url': '/search?name=' + searchText, 'success': onSuccess});
  });

});
