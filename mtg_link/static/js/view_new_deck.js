$(document).on('ready', function onReady(evt) {
  var quickViewInput = $('#quick-view-input');
  quickViewInput.on('keyup', function(evt) {
    var currentText = quickViewInput.val();
    var callback = function(resp) {
      if (resp.success) {
        $('#quick-view-image').attr('src', resp.imageUrl);
      }
    };
    var payload = {
      'url': '/search?name=' + $('#quick-view-input').val(),
      'success': callback
    };
    $.get(payload);
  });

  var newDeckSubmitButton = $('#new-deck-submit-button');
  newDeckSubmitButton.on('click', function(evt) {
    var deckText = $('.new-deck-textarea').val();
    var deckName = $('deck-name-input').val();
    var callback = function(resp) {
      if (resp.success) {
        alert('Deck ' + resp.deckName + ' saved successfully!');
      }
    };
    var payload = {
      'url': '/api/new-deck',
      'success': callback,
      'data': {'text': deckText, 'deckName': deckName}
    }
    $.post(payload);
  });
});
