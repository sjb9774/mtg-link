$(document).on('ready', function(evt) {
  var linkRows = $('.link-row');
  linkRows.on('click', function(evt) {
    var target = $(evt.currentTarget);
    redirect(target.attr('data-href'));
  });
});
