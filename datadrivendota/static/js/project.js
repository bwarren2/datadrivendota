/* Project specific Javascript goes here. */
$(function () {
    'use strict';
    Messenger.options = {
        extraClasses: 'messenger-fixed messenger-on-top',
        theme: 'future'
    };

    var clippables = new Clipboard('.clippable');

    clippables.on('success', function(e) {
        e.clearSelection();
        console.log('Copied!')
        console.log(e);
        Messenger().post({
          message: 'Copied '+ e.text,
          type: 'info',
          hideAfter: 2
        });

    });

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
        .done(function() {})
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

                $('.click-selector').addClass('clicked');
                $('.click-selector').text('Unselect');

                var hero_class = window.jsUtils.convertToSlug(
                    $('.select2-selection__rendered').html().trim()
                );
                var str = '.nv-point:not(.'+hero_class+'), .discreteBar:not(.'+hero_class+')';

                var selection = d3.selectAll(str)
                .transition()
                .duration(500)
                .style('opacity',0)
                .transition().duration(0)
                .style('visibility', 'hidden');

            } else {
                // We have to clear the option each time because select2 is fine to add new instances on top of old ones.
                // $('#combo-select option').remove().trigger("change");
                var str = '.nv-point, .discreteBar';
                d3.selectAll(str)
                .transition()
                .duration(500)
                .style('opacity',1)
                .style('visibility', 'visible');

                $('.click-selector').removeClass('clicked');
                $('.click-selector').text('Select');

            }
        });
    }


    function formatPms (log) {
      if (log.loading) return "";

      var markup = "<div class='select2-result-log clearfix'>" +
        "<div class='select2-result-pms__meta'>" +
          "<div class='select2-result-pms__title'>" + log.name+", M#"+log.match_id + "</div>"+
          "</div></div>";

      return markup;
    }

    function formatPmsSelection (log) {
      return log.name+', M#'+log.match_id;
    }


    var pms_select2 = function(selector, multiple){

        $(selector).select2({
          ajax: {
            url: "/rest-api/parse-shards/",
            dataType: 'json',
            delay: 250,
            multiple: multiple,
            data: function (params) {
              return {
                match_id: params.term, // search term
                page: params.page
              };
            },
            processResults: function (data, params) {
              params.page = params.page || 1;

              return {
                results: data,
                pagination: {
                  more: (params.page * 30) < data.total_count
                }
              };
            },
            cache: true
          },
          escapeMarkup: function (markup) { return markup; },
          minimumInputLength: 6,
          templateResult: formatPms,
          templateSelection: formatPmsSelection

        });
    }

    window.inputs = {};
    window.inputs.pms_select2 = pms_select2;

    window.comboBox = comboBox;

    window.comboBox();

    $('#combo-select').select2({
        ajax: {
          delay: 250,
          url:'/api/combobox_tags/',
          processResults: function (data) {
            var res = data.results.map(function (elt) {
             return {id: elt.label, text: elt.value}; }
            )
            return {results: res};
          },
        },
        minimumInputLength: 2,
    });


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

    /**
     * Handling the play/pause button.
     */
    $('#pause-play').click(function() {
        var icon = $(this).children('span');
        if (icon.hasClass('glyphicon-play')) {
            $(window).trigger('play');
            icon.removeClass('glyphicon-play').addClass('glyphicon-pause');
        } else {
            $(window).trigger('pause');
            icon.addClass('glyphicon-play').removeClass('glyphicon-pause');
        }
    });
    $('#back-animation').click(function() {
        $(window).trigger('back');
    });
    $('#forward-animation').click(function() {
        $(window).trigger('forward');
    });

    window.jsUtils.getParameterByName = function(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    var playback = function(start, end, idx, formatter){

        var diff = end - start;

        var update = function(tick){
          idx = (idx + tick).mod(end + 1);
          $(window).trigger('update', idx);
        }

        $('#progress-bar-current').html(0);

        if (formatter!==undefined) {
            $('#progress-bar-max').html(formatter(end));
        }else{
            $('#progress-bar-max').html(end);
        }




        // Set up timing controls
        var timer;
        function runner() {
          update(1);
          timer = setTimeout(runner, 1000);
        }
        $(window).on('play', function(){
          runner();
        });
        $(window).on('pause', function(){
           clearTimeout(timer);
        });
        $(window).on('forward', function(){
          update(1);
        });
        $(window).on('back', function(){
          update(-1);
        });
        var isDragging = false;
        $('#progress-bar').mousedown(function (evt) {
          isDragging = true;
          // Brittle af
          var progressBarWidth = $(evt.currentTarget).children('span').width();
          idx = ((evt.offsetX / progressBarWidth) * diff) | 0;
          $(window).trigger('update', idx);
        }).mousemove(function (evt) {
          if (isDragging) {
            // Brittle af
            var progressBarWidth = $(evt.currentTarget).children('span').width();
            idx = ((evt.offsetX / progressBarWidth) * diff) | 0;
            $(window).trigger('update', idx);
          }
        }).mouseup(function (evt) {
          isDragging = false;
        });

        $(window).on('update', function (evt, idx) {
          // Progbar
          var width = (idx / diff) * 100;
          $('#progress-bar').css('width', '' + width + '%');
          $('#progress-bar').attr('aria-valuenow', width);
          // Update progress bar time.
          // @TODO make this show time, not ticks?
          if (formatter!==undefined) {
              $('#progress-bar-current').html(formatter(idx));
          }else{
              $('#progress-bar-current').html(idx);
          }


        });

    }
    window.jsUtils.playback = playback;

});

Number.prototype.mod = function(n) {
    return (( this % n) + n) % n;
}

String.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    if (sec_num < 0) {
        sec_num = Math.abs(sec_num);
        var prefix="-";
    }else{
        var prefix="";
    }
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    var time    = hours+':'+minutes+':'+seconds;
    return prefix+time;
}
