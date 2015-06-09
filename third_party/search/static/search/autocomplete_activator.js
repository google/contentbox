/*
 * This file enables the auto-complete feature. To be autocompleted, an
 * input field has to include the src attribute to indicate the path
 * to the live_search view, which returns a json file with data.
 * Moreover, to enable the redirection to the corresponding
 * page of the selected item, this path must be followed by '/redirect'
 * (without trailing slash).
 */

$(document).ready(function() {
	$('#search #id_box').livequery(function() {
		var options = ['multipleValues', 'selectFirst', 'autoFill', 'mustMatch',
									 'matchContains'];
		for (var i=0; i < options.length; i++)
			eval('var ' + options[i] + ' = false;');

		for (i=0; i < options.length; i++)
			if ($(this).hasClass(options[i].replace(/[A-Z]/,
					'-' + options[i].match(/[A-Z]/)[0].toLowerCase())))
				eval(options[i] + ' = true;');

		// append djangos (patched via aep) help text
		var help_text = $($.Autocompleter.defaults.help_text);
		if ($('form', $(this).parents()).length) {
			if ($(this).next().length && $(this).next().hasClass('help-text'))
				help_text.append($(this).next().clone(true));
		}
		//TODO: extend the options with options above
		$(this).autocomplete($(this).attr('src'), {
			cacheLength : 10,
			max: 10,
			width: $('#id_box').outerWidth(),
			scrollHeight: 250,
			multiple: multipleValues,
			selectFirst: selectFirst,
			autoFill: autoFill,
			mustMatch: mustMatch,
			matchContains: matchContains,
			parse: function(data) { return data; },
			dataType: 'json',
			formatItem: function(data, i, n, value) { return value; },
			help_text: help_text,
			extraParams: {
                'languages':  function(){return $('#id_language').val();},
                'content_types':  function(){return $('#id_content_type').val();}
            }
		});
		$(this).result(function(event, data, formatted) {
			if (data["link"]) {
				document.location.href=data.link;
			}
		});
		$(this).addClass('autocompleting');
	});
});
