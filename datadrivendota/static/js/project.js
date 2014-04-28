/* Project specific Javascript goes here. */

$(function () {
  Messenger.options = {
      extraClasses: 'messenger-fixed messenger-on-top',
      theme: 'future'
  }

  function format(state) {
      return state.label;
  }

  function singleInitSeelction(element, callback) {
    var data = {id: element.val(), text: element.val()};
    callback(data);
  }

  function multpleInitSelection(element, callback) {
      var data = [];
      $(element.val().split(",")).each(function () {
          data.push({id: this, text: this});
      });
      callback(data);
  }

  function ajax_select2ify(selector, multiple, placeholder, api_endpoint) {
    if (multiple) {
      var initSelectionFunction = multpleInitSelection;
    } else {
      var initSelectionFunction = singleInitSeelction;
    }

    $(selector).select2({
      multiple: multiple,
      placeholder: placeholder,
      initSelection: initSelectionFunction,
      ajax: {
        url: api_endpoint,
        data: function (term) {
          return {term: term};
        },
        results: function (data, page) {
          return {
            results: data.map(function (elt) { return {id: elt.label, text: elt.label}; })
          };
        },
        formatResult: format,
        formatSelection: format
      }
    });
  }

  $('#contact-link').click(function () {
    if ($('#IntercomDefaultWidget').length) {
      $('#IntercomDefaultWidget').click();
      return false;
    } else {
      return true;
    }
  });

  $('.info').tooltip();
  // $("#myTable").tablesorter();

  $('input[type=checkbox]:checked').parent().addClass('active');
  $('input[type=checkbox]').change(function (evt) {
    $(evt.target).parent().toggleClass('active');
  });

  $(".datepicker").datepicker({
    dateFormat: 'yy-mm-dd'
  });

  $('select').select2({
    width: "100%"
  });

  ajax_select2ify('.single-player-tags', false, "One Player", "/players/api/getplayers");
  ajax_select2ify('.multi-player-tags', true, "One or more Players", "/players/api/getplayers");
  ajax_select2ify('.single-hero-tags', false, "One Hero", "/heroes/api/getheroes");
  ajax_select2ify('.multi-hero-tags', true, "One or more Heroes", "/heroes/api/getheroes");
  ajax_select2ify('.multi-match-tags', true, "One or more Matches", "/matches/api/getmatches");
  ajax_select2ify('.single-match-tags', true, "One Match", "/matches/api/getmatches");

  /* gettext library */

  var catalog = new Array();

  function pluralidx(n) {
    var v = (n != 1);
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  }

  catalog['%(sel)s of %(cnt)s selected'] = ['',''];
  catalog['%(sel)s of %(cnt)s selected'][0] = '%(sel)s of %(cnt)s selected';
  catalog['%(sel)s of %(cnt)s selected'][1] = '%(sel)s of %(cnt)s selected';
  catalog['6 a.m.'] = '6 a.m.';
  catalog['Available %s'] = 'Available %s';
  catalog['Calendar'] = 'Calendar';
  catalog['Cancel'] = 'Cancel';
  catalog['Choose a time'] = 'Choose a time';
  catalog['Choose all'] = 'Choose all';
  catalog['Choose'] = 'Choose';
  catalog['Chosen %s'] = 'Chosen %s';
  catalog['Click to choose all %s at once.'] = 'Click to choose all %s at once.';
  catalog['Click to remove all chosen %s at once.'] = 'Click to remove all chosen %s at once.';
  catalog['Clock'] = 'Clock';
  catalog['Filter'] = 'Filter';
  catalog['Hide'] = 'Hide';
  catalog['January February March April May June July August September October November December'] = 'January February March April May June July August September October November December';
  catalog['Midnight'] = 'Midnight';
  catalog['Noon'] = 'Noon';
  catalog['Now'] = 'Now';
  catalog['Remove all'] = 'Remove all';
  catalog['Remove'] = 'Remove';
  catalog['S M T W T F S'] = 'S M T W T F S';
  catalog['Show'] = 'Show';
  catalog['This is the list of available %s. You may choose some by selecting them in the box below and then clicking the "Choose" arrow between the two boxes.'] = 'This is the list of available %s. You may choose some by selecting them in the box below and then clicking the "Choose" arrow between the two boxes.';
  catalog['This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the "Remove" arrow between the two boxes.'] = 'This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the "Remove" arrow between the two boxes.';
  catalog['Today'] = 'Today';
  catalog['Tomorrow'] = 'Tomorrow';
  catalog['Type into this box to filter down the list of available %s.'] = 'Type into this box to filter down the list of available %s.';
  catalog['Yesterday'] = 'Yesterday';
  catalog['You have selected an action, and you haven\'t made any changes on individual fields. You\'re probably looking for the Go button rather than the Save button.'] = 'You have selected an action, and you haven\'t made any changes on individual fields. You\'re probably looking for the Go button rather than the Save button.';
  catalog['You have selected an action, but you haven\'t saved your changes to individual fields yet. Please click OK to save. You\'ll need to re-run the action.'] = 'You have selected an action, but you haven\'t saved your changes to individual fields yet. Please click OK to save. You\'ll need to re-run the action.';
  catalog['You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.'] = 'You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.';


  function gettext(msgid) {
    var value = catalog[msgid];
    if (typeof(value) == 'undefined') {
      return msgid;
    } else {
      return (typeof(value) == 'string') ? value : value[0];
    }
  }

  function ngettext(singular, plural, count) {
    value = catalog[singular];
    if (typeof(value) == 'undefined') {
      return (count == 1) ? singular : plural;
    } else {
      return value[pluralidx(count)];
    }
  }

  function gettext_noop(msgid) {
    return msgid;
  }

  function pgettext(context, msgid) {
    var value = gettext(context + '\x04' + msgid);
    if (value.indexOf('\x04') != -1) {
      value = msgid;
    }
    return value;
  }

  function npgettext(context, singular, plural, count) {
    var value = ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
    if (value.indexOf('\x04') != -1) {
      value = ngettext(singular, plural, count);
    }
    return value;
  }

  function interpolate(fmt, obj, named) {
    if (named) {
      return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
    } else {
      return fmt.replace(/%s/g, function(match){return String(obj.shift())});
    }
  }

  /* formatting library */

  var formats = new Array();

  formats['DATETIME_FORMAT'] = 'N j, Y, P';
  formats['DATE_FORMAT'] = 'N j, Y';
  formats['DECIMAL_SEPARATOR'] = '.';
  formats['MONTH_DAY_FORMAT'] = 'F j';
  formats['NUMBER_GROUPING'] = '3';
  formats['TIME_FORMAT'] = 'P';
  formats['FIRST_DAY_OF_WEEK'] = '0';
  formats['TIME_INPUT_FORMATS'] = ['%H:%M:%S', '%H:%M'];
  formats['THOUSAND_SEPARATOR'] = ',';
  formats['DATE_INPUT_FORMATS'] = ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'];
  formats['YEAR_MONTH_FORMAT'] = 'F Y';
  formats['SHORT_DATE_FORMAT'] = 'm/d/Y';
  formats['SHORT_DATETIME_FORMAT'] = 'm/d/Y P';
  formats['DATETIME_INPUT_FORMATS'] = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M', '%m/%d/%Y', '%m/%d/%y %H:%M:%S', '%m/%d/%y %H:%M', '%m/%d/%y', '%Y-%m-%d %H:%M:%S.%f'];

  function get_format(format_type) {
    var value = formats[format_type];
    if (typeof(value) == 'undefined') {
      return format_type;
    } else {
      return value;
    }
  }

  $('#hero-filter-select').change(function () {
    var role_select = $(this).val();
    if (!!role_select) {
      $('.col-md-2:not(.' + role_select + ')').fadeOut();
      $('.col-md-2.' + role_select).fadeIn();
    } else {
      $('.col-md-2').fadeIn();
    }
  });

});

window.jsUtils = {}

function scorebarToggles(){
  $('.scorebar').hide();
  $('#show-score').click(function(){$('.scorebar').fadeIn('fast');});
  $('#hide-score').click(function(){$('.scorebar').fadeOut('fast');});
}

window.jsUtils.scorebarToggles = scorebarToggles

function convertToSlug(Text)
{
    return Text
        .toLowerCase()
        .replace(/ /g,'-')
        .replace(/[^\w-]+/g,'')
        ;
}

var getVals = function(obj){
   var vals = [];
   for(var key in obj){
      vals.push(obj[key]);
   }
   return vals;
}

function apiHit (targetDestination, api_url, api_params, callback){
  show_progress_bar(targetDestination);
  $.get(
          api_url,
          api_params,
          function(json){
            d3.json(json['url'],function(source){
              var input_data = source;
              window.d3ening.plot(source, targetDestination)
            });
          },
          'json'
        )
    .done(function() {
      if (callback){
        callback();
      }
    })
    .fail(function() {})
    .always(function() {
      $(targetDestination + ' .progress-bar').remove()
      $(targetDestination + ' #progbar_loading').remove()
    });
}

window.apiHit = apiHit;

function show_progress_bar (identifier) {
      var progressbar = $("<div>");
      progressbar.attr('id', 'progbar_loading');
      progressbar.addClass("progress");
      progressbar.addClass("progress-striped active");

      var progressbar_inner = $("<div>");
      progressbar_inner.addClass("progress-bar");
      progressbar_inner.attr('role', "progressbar");
      progressbar_inner.attr('aria-valuenow', "100");
      progressbar_inner.attr('aria-valuemin', "0");
      progressbar_inner.attr('aria-valuemax', "100");
      progressbar_inner.css('width', '100%');

      progressbar.append(progressbar_inner);

      $(identifier).append(progressbar);
}
