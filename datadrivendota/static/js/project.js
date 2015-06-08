/* Project specific Javascript goes here. */
$(function () {
  'use strict';
  Messenger.options = {
      extraClasses: 'messenger-fixed messenger-on-top',
      theme: 'future'
  };

  $('#combo-select').select2({
    ajax: {
      delay: 250,
      url:'/matches/api/combobox_tags/',
      processResults: function (data) {
        var res = data.results.map(function (elt) {
         return {id: elt.label, text: elt.value}; }
        )
        return {results: res};
      },
    },
    minimumInputLength: 3,
  });


  // Handle select2 stuff
  // function format(state) {
  //     return state.label;
  // };

  // function singleInitSelection(element, callback) {
  //   var data = {id: element.val(), text: element.val()};
  //   callback(data);
  // }

  // function multipleInitSelection(element, callback) {
  //     var data = [];
  //     $(element.val().split(',')).each(function () {
  //         data.push({id: this, text: this});
  //     });
  //     callback(data);
  // }

  // function ajax_select2ify(selector, multiple, placeholder, api_endpoint, cb) {

  //   if (multiple) {
  //     var initSelectionFunction = multipleInitSelection;
  //   } else {
  //     var initSelectionFunction = singleInitSelection;
  //   }

  //     // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
  //     // minimumInputLength: 1,
  //     // templateResult: formatRepo, // omitted for brevity, see the source of this page
  //     // templateSelection: formatRepoSelection // omitted for brevity, see the source of this page


  //     // multiple: multiple,
  //     // placeholder: placeholder,
  //     // initSelection: initSelectionFunction,
  //     // ajax: {
  //     //   url: api_endpoint,
  //     //   data: function (term) {
  //     //     return {'search': term};
  //     //   },
  //     //   results: cb,
  //     //   formatResult: format,
  //     //   formatSelection: format
  //     // }
  //   });
  // }

  // // ajax_select2ify(
  // //   , false, 'One Selector', ,
  //   function (data, page) {
  //     return {
  //       results: data.results.map(
  //         function (elt) { return {id: elt.label, text: elt.value}; }
  //       )
  //     };
  //   }

  // );




  // Not all of these form fields are used now.
  // But it will be easier to rip them out after the refactor.
  // ajax_select2ify(
  //   '.single-player-tags', false, 'One Player', '/rest-api/players',
  //   function (data, page) {
  //     return {
  //       results: data.map(function (elt) { return {id: elt.steam_id, text: elt.persona_name}; })
  //     };
  //   }
  // );
  // ajax_select2ify(
  //   '.multi-player-tags', true, 'One or more Players', '/rest-api/players',
  //   function (data, page) {
  //     return {
  //       results: data.map(function (elt) { return {id: elt.steam_id, text: elt.persona_name}; })
  //     };
  //   }
  // );
  // ajax_select2ify(
  //   '.single-hero-tags', false, 'One Hero', '/rest-api/heroes',
  //   function (data, page) {
  //     return {
  //       results: data.map(function (elt) { return {id: elt.steam_id, text: elt.name}; })
  //     };
  //   }
  // );
  // ajax_select2ify(
  //   '.multi-hero-tags', true, 'One or more Heroes', '/rest-api/heroes',
  //   function (data, page) {
  //     return {
  //       results: data.results.map(function (elt) { return {id: elt.steam_id, text: elt.name}; })
  //     };
  //   }

  // );
  // ajax_select2ify(
  //   '.single-match-tags', false, 'One Match', '/rest-api/matches',
  //   function (data, page) {
  //     return {
  //       results: data.map(function (elt) { return {id: elt.steam_id, text: elt.steam_id}; })
  //     };
  //   }

  // );
  // ajax_select2ify(
  //   '.multi-match-tags', true, 'One or more Matches', '/rest-api/matches',
  //   function (data, page) {
  //     return {
  //       results: data.results.map(function (elt) { return {id: elt.steam_id, text: elt.steam_id}; })
  //     };
  //   }
  // );
  // ajax_select2ify(
  //   '.single-team-tags', false, 'One Team', '/rest-api/items',
  //   function (data, page) {
  //     return {
  //       results: data.map(function (elt) { return {id: elt.steam_id, text: elt.name}; })
  //     };
  //   }
  // );
  // ajax_select2ify(
  //   '.single-league-tags', false, 'One League', '/rest-api/leagues',
  //   function (data, page) {
  //     return {
  //       results: data.map(function (elt) { return {id: elt.steam_id, text: elt.name}; })
  //     };
  //   }
  // );


  $('#contact-link').click(function () {
    if ($('#IntercomDefaultWidget').length) {
      $('#IntercomDefaultWidget').click();
      return false;
    } else {
      return true;
    }
  });

  $('.info').tooltip();

  $('input[type=checkbox]:checked').parent().addClass('active');
  $('input[type=checkbox]').change(function (evt) {
    $(evt.target).parent().toggleClass('active');
  });

  $('.datepicker').datepicker({
    dateFormat: 'yy-mm-dd'
  });

  window.jsUtils = {};

  function scorebarToggles(){
    $('.scorebar').hide();
    $('.win-glyph').hide();
    $('#show-score').click(function(){
      $('.win-glyph').fadeIn('fast');
      $('.scorebar').fadeIn('fast');
    });
    $('#hide-score').click(function(){
      $('.win-glyph').fadeOut('fast');
      $('.scorebar').fadeOut('fast');
    });
  }

  window.jsUtils.scorebarToggles = scorebarToggles;


  function secondstotime(secs){
      var t = new Date(1970,0,1);
      t.setSeconds(secs);
      var s = t.toTimeString().substr(0,8);
      if(secs > 86399)
        s = Math.floor((t - Date.parse('1/1/70')) / 3600000) + s.substr(2);
      return s;
  }
  window.jsUtils.secondstotime = secondstotime;

  function convertToSlug(Text)
  {
      return Text
          .toLowerCase()
          .replace(/ /g,'-')
          .replace(/[^\w-]+/g,'')
          ;
  };

  window.jsUtils.convertToSlug = convertToSlug;

  var getVals = function(obj){
     var vals = [];
     for(var key in obj){
        vals.push(obj[key]);
     }
     return vals;
  };

  function apiHit (targetDestination, api_url, api_params, callback){
    show_progress_bar(targetDestination);
    $.get(
            api_url,
            api_params,
            function(json){
              d3.json(json['url'],function(source){
                var input_data = source;
                window.d3ening.plot(source, targetDestination, callback)
              });
            },
            'json'
          )
      .done(function() {
      })
      .fail(function() {})
      .always(function() {
        $(targetDestination + ' .progress-bar').remove()
        $(targetDestination + ' #progbar_loading').remove()
      });
  }

  window.apiHit = apiHit;

  function comboBox(){
    d3.selectAll('.click-selector')
      .on('click', function(d){
        if (!$('.click-selector').hasClass('clicked')){
          var str = '.data-toggleable:not(.'+window.jsUtils.convertToSlug(
            $('span#combobox .select2-chosen').text()
          )+')';
          selection = d3.selectAll(str)
          .transition()
          .duration(500)
          .style('opacity',0)
          .transition().duration(0)
          .style('visibility', 'hidden');

          $('.click-selector').addClass('clicked');
          $('.click-selector').text('Unselect');

        } else {
          var str = '.data-toggleable';
          d3.selectAll(str)
          .transition()
          .duration(500)
          .style('opacity',1)
          .style('visibility', 'visible');

          $('.click-selector').removeClass('clicked');
          $('.click-selector').text('Select');

        }
      }
    );
  }

  window.comboBox = comboBox;



  function show_progress_bar (identifier) {
        var progressbar = $('<div>');
        progressbar.attr('id', 'progbar_loading');
        progressbar.addClass('progress');
        progressbar.addClass('progress-striped active');

        var progressbar_inner = $('<div>');
        progressbar_inner.addClass('progress-bar');
        progressbar_inner.attr('role', 'progressbar');
        progressbar_inner.attr('aria-valuenow', '100');
        progressbar_inner.attr('aria-valuemin', '0');
        progressbar_inner.attr('aria-valuemax', '100');
        progressbar_inner.css('width', '100%');

        progressbar.append(progressbar_inner);

        $(identifier).append(progressbar);
  }

  window.jsUtils.heroAttribute = function(attr, level, hero){
    switch(attr){
      case 'strength':
       return hero.strength + hero.strength_gain * level - 1;
      case 'intelligence':
       return hero.intelligence + hero.intelligence_gain * level - 1;
      case 'agility':
       return hero.agility + hero.agility_gain * level - 1;
      default:
       return 0
    }
  }
});

