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
                    return {id: elt.label, text: elt.value};
                })
                return {results: res};
            },
        },
        minimumInputLength: 3,
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

                var str = '.nv-point:not(.'+window.jsUtils.convertToSlug(
                    $('#combo-select').text().trim()
                )+')';

                // var str = '.nv-point:not(.nv-point-0)';
                var selection = d3.selectAll(str)
                .transition()
                .duration(500)
                .style('opacity',0)
                .transition().duration(0)
                .style('visibility', 'hidden');

            } else {

                var str = '.nv-point';
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

});

