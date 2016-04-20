(function() {
  'use strict';

  $(document).ready(function() {
    $('#match-select form').submit(function(evt) {
      evt.preventDefault();
      var data = {
        limit: 5
      };
      $('#match-select form').serializeArray().map(function(elem) {
        data[elem.name] = elem.value;
      });
      $.ajax('/rest-api/matches/', {
        data: data,
        success: function(matches) {
          $('#filtered-matches').html('');
          $.each(matches, function(index, elem) {
            var template = `<li><a href="/matches/${elem.steam_id}/" target="_blank">${elem.steam_id}</a> <i class="glyphicon glyphicon-copy clippable" title="Copy match id" data-clipboard-text="${elem.steam_id}"></i></li>`;
            $('#filtered-matches').append(
              $(template)
            );
          });
          $('#match-select').modal('hide');
        },
      });
    });
  });
})();
