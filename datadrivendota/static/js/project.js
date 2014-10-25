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
            results: data.map(function (elt) { return {id: elt.value, text: elt.label}; })
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
  ajax_select2ify('.single-match-tags', false, "One Match", "/matches/api/getmatches");
  ajax_select2ify('.multi-match-tags', true, "One or more Matches", "/matches/api/getmatches");
  ajax_select2ify('.single-team-tags', false, "One Team", "/teams/api/getteams");
  ajax_select2ify('.single-league-tags', false, "One League", "/leagues/api/getleagues");
  ajax_select2ify('.combobox-tags', false, "One Selector", "/matches/api/gettags");

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

window.jsUtils.scorebarToggles = scorebarToggles

function convertToSlug(Text)
{
    return Text
        .toLowerCase()
        .replace(/ /g,'-')
        .replace(/[^\w-]+/g,'')
        ;
}

window.jsUtils.convertToSlug = convertToSlug

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
    .on('click',function(d){
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
        $('.click-selector').addClass('clicked')
        $('.click-selector').text('Unselect')
      }else{
        var str = '.data-toggleable';
        d3.selectAll(str)
        .transition()
        .duration(500)
        .style('opacity',1)
        .style('visibility', 'visible');
        $('.click-selector').removeClass('clicked')
        $('.click-selector').text('Select')
      }
    }
  );
}

window.comboBox = comboBox;

var new_index = function(dataset, i){
  if(i==dataset.length){
    return(0);
  }
  else{
    return(i+1)
  }
}

var side_progress_line = function(dataset, target_selector, bind_button, callback){

  initial_fract = 3
  var initial_count = Math.round(dataset.length/initial_fract);

  var margin = {top: 15, right: 15, bottom: 25, left: 60},
      width = 400 - margin.right,
      height = 400 - margin.top - margin.bottom;

  data_slice = dataset.slice(0, initial_count)

  var x = d3.scale.linear()
      .domain([
        d3.min(data_slice, function(d){return(d['times'])}),
        d3.max(data_slice, function(d){return(d['times'])}),
      ])
      .range([0, width]);

  var y = d3.scale.linear()
      .domain([
        d3.min(data_slice, function(d){return(
          Math.min(
            d['radiant'],
            d['dire'],
            d['difference']
            )
          )
        }),
        d3.max(data_slice, function(d){return(
          Math.max(
            d['radiant'],
            d['dire'],
            d['difference']
            )
          )
        })
      ])
      .range([height, 0]);

  var radiantline = d3.svg.line()
      .interpolate("basis")
      .x(function(d, i) { return x(d['times']); })
      .y(function(d, i) { return y(d['radiant']); });
  var direline = d3.svg.line()
      .interpolate("basis")
      .x(function(d, i) { return x(d['times']); })
      .y(function(d, i) { return y(d['dire']); });
  var diffline = d3.svg.line()
      .interpolate("basis")
      .x(function(d, i) { return x(d['times']); })
      .y(function(d, i) { return y(d['difference']); });

  var svg = d3.select(target_selector).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .style("margin-left", -margin.left + "px")
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("defs").append("clipPath")
      .attr("id", "clip")
      .append("rect")
      .attr("width", width)
      .attr("height", height);

  var xaxis = svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(x.axis = d3.svg.axis().scale(x).orient("bottom"));

      xaxis.append("text")
        .attr("class", "x-axis-label")
        .attr("y", -16)
        .attr("x", width)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text('Time');


  var yaxis = svg.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate(0,0)")
      .call(y.axis = d3.svg.axis().scale(y).orient("left"));

      yaxis.append("text")
      .attr("class", "y-axis-label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text('Sum Team Health');


  var radiant_path = svg.append("g")
      .attr("clip-path", "url(#clip)")
      .append("svg:path")
      .data([data_slice])
      .attr("class", "radiant-line progress-line")

  var dire_path = svg.append("g")
      .attr("clip-path", "url(#clip)")
      .append("svg:path")
      .data([data_slice])
      .attr("class", "dire-line progress-line")

  var diff_path = svg.append("g")
      .attr("clip-path", "url(#clip)")
      .append("svg:path")
      .data([data_slice])
      .attr("class", "difference-line progress-line")

  idx = initial_count


  function tick(dataset, idx) {
    idx = new_index(dataset, idx)
    if(idx<dataset.length){
      data_slice.push(dataset[idx])
    }else{
      return
    }

    // update the domains
    x.domain([
      d3.min(data_slice, function(d){return(d['times'])}),
      d3.max(data_slice, function(d){return(d['times'])}),
    ]);
    y.domain([
        d3.min(data_slice, function(d){return(
          Math.min(
            d['radiant'],
            d['dire'],
            d['difference']
            )
          )
        }),
        d3.max(data_slice, function(d){return(
          Math.max(
            d['radiant'],
            d['dire'],
            d['difference']
            )
          )
        })
    ])


    // redraw the line
    svg.select(target_selector+" .radiant-line")
        .attr("d", radiantline)
        .attr("transform", null);
    svg.select(target_selector+" .dire-line")
        .attr("d", direline)
        .attr("transform", null);
    svg.select(target_selector+" .difference-line")
        .attr("d", diffline)
        .attr("transform", null);

    // // slide the x-axis left
    xaxis.transition()
        .duration(duration)
        .ease("linear")
        .call(x.axis);

    // // move the y axis
    yaxis.transition()
        .duration(duration)
        .ease("linear")
        .call(y.axis)
        .each("end", tick(dataset, idx));


    // // pop the old data point off the front
    data_slice.shift();
  }


  $(bind_button).click(function(){
    tick(dataset, idx);
  }
  // if(typeof callback === 'undefined'){
  //   callback()
  // }
}

window.side_progress_line = side_progress_line

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
