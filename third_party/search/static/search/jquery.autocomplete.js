/*
License: http://gae-full-text-search.appspot.com/license
Copyright 2009 Waldemar Kornewald & Thomas Wanschik GbR
Use/redistribution without explicit permission (e.g., a granted license) is prohibited.

This autocomplete jQuery plugin is a customized version based on work by Dylan Verheul, Dan G. Switzer, Anjesh Tuladhar, Jörn Zaefferer
*/

;(function($) {

$.fn.extend({
	autocomplete: function(urlOrData, options) {
		var isUrl = typeof urlOrData == "string";
		options = $.extend({}, $.Autocompleter.defaults, {
			url: isUrl ? urlOrData : null,
			data: isUrl ? null : urlOrData,
			delay: isUrl ? $.Autocompleter.defaults.delay : 10,
			max: options && !options.scroll ? 10 : 150
		}, options);

				// options.lengthPerCacheKey should be the max number of results returned by
				// the server
				if (!options.lengthPerCacheKey)
						options.lengthPerCacheKey = options.max;
				else {
						options.lengthPerCacheKey = (options.lengthPerCacheKey < options.max) ?
								options.max : options.lengthPerCacheKey;
				}
		// if highlight is set to false, replace it with a do-nothing function
		options.highlight = options.highlight || function(value) { return value; };

		// if the formatMatch option is not specified, then use formatItem for backwards compatibility
		options.formatMatch = options.formatMatch || options.formatItem;

		return this.each(function() {
			new $.Autocompleter(this, options);
		});
	},
	result: function(handler) {
		return this.bind("result", handler);
	},
	search: function(handler) {
		return this.trigger("search", [handler]);
	},
	flushCache: function() {
		return this.trigger("flushCache");
	},
	setOptions: function(options){
		return this.trigger("setOptions", [options]);
	},
	unautocomplete: function() {
		return this.trigger("unautocomplete");
	}
});

$.Autocompleter = function(input, options) {

	var KEY = {
		UP: 38,
		DOWN: 40,
		DEL: 46,
		TAB: 9,
		RETURN: 13,
		ESC: 27,
		COMMA: 188,
		PAGEUP: 33,
		PAGEDOWN: 34,
		BACKSPACE: 8,
		LEFT_ARROW: 37,
		RIGHT_ARROW: 39,
		HOME: 36,
		END: 35,
		SHIFT: 16
	};

	// Create $ object for input element
	var $input = $(input).attr("autocomplete", "off").addClass(options.inputClass);

	var timeout;
	var previousValue = '';
	var cache = $.Autocompleter.Cache(options);
	var hasFocus = 0;
	var lastKeyPressCode;
	var config = {
		mouseDownOnSelect: false,
		from_selection: false
	};
	var select = $.Autocompleter.Select(options, input, selectCurrent, config);

	// function to display facebook-style results (help_text, no results found, ...)
	var showSpecialResult = function(type) {
		select.init();
		select.show(type);
	};

	// checks if mouse is over the dropdown arrow
	var on_dropdownarrow = function(event) {
		return ($input.offset().left + $input.innerWidth() - parseInt($input.css('padding-right')) < event.pageX
				&& $input.offset().left + $input.innerWidth() > event.pageX &&
				$input.offset().top + $input.innerHeight() > event.pageY &&
				$input.offset().top < event.pageY);
	};

	// function used to display the complete list, used for the dropdown option
	var open_complete_list = function () {
		var data = cache.load('');
		if (data && data.length) {
			select.display(data, '');
			// do not show the result list, if input has been removed
			if($('body', $input.parents()).get(0) && hasFocus)
				select.show();
		}

		// mark selected value to allow immediate typing of new words
		setTimeout(function() {
			$.Autocompleter.Selection(input, 0, input.value.length);
		}, 100);
	};
	/* If options.dropdown is defined, add
		 an image button next to the autocomplete field
		 that will open the autocomplete list like
		 a dropdown input
	*/
	if (options.dropdown) {
		// the images should have a size of (20x20)px
		options.dropdown = (options.dropdown === true) ? ['dropdownarrow.png',
			'dropdownarrow over.png'] : options.dropdown;
		// always show the drop down list
		options.minChars = 0;
		// for a select-list the user can only select exactly one item!
		options.multiple = false;
		 // for a select-list the user has to type in the exact word!
		options.mustMatch = true;
		// do never use matchContains with autoFill!
		if (options.matchContains)
			options.autoFill = false;
		// TODO: Use data.length or something like this
		// show all results
		options.max = $.Autocompleter.defaults.max;
		// case insensitive!
		options.matchCase = false;
		options.selectFirst = true;

		// preload images
		new Image().src = options.dropdown[1];
		new Image().src = options.dropdown[1];

		$input.addClass('dropdown').css({
			'background': 'white url(' + options.dropdown[0] + ') center right no-repeat',
			'padding-right': '20px'
		});

		$input.mousedown(function(event) {
			if (on_dropdownarrow(event)) {
				if (select.visible()) {
					// list is visible, so the click will hide it but check if value is supported, so call
					// use hideResultsNow instead of select.hide!
					hideResultsNow('whole-word');
					// TODO: prevent mousedown on body?
					// return false;
				}
				else if (hasFocus) {
					// if hasFocus is false, focus will be fired after this
					// mousedown causing the list to open,
					// list is hidden, so the click will show it.
					open_complete_list();
					// enable selection of results
					return false;
				}
			}
			else if (hasFocus && !select.visible()) {
				open_complete_list();
				// enable selection of results
				return false;
			}
		}).mousemove(function(event) {
			if(on_dropdownarrow(event))
				$input.css({
					'cursor': 'default',
					'background': 'white url(' + options.dropdown[1] + ') center right no-repeat'
				});
			else {
				if (!select.visible())
					$input.css('background',
							'white url(' + options.dropdown[0] + ') center right no-repeat');
				$input.css('cursor', 'text');
			}
		}).mouseleave(function(event) {
			if (!select.visible())
				$input.css({
					'background': 'white url(' + options.dropdown[0] + ') center right no-repeat'
			});
		}).mouseup(function () {
			config.mouseDownOnSelect = false;
			// return false;
		});
	}

	// set focus again if mousedown was fired on an result item but no mouseup
//  $(document).mouseup(function() {
//    if (config.mouseDownOnSelect) {
//      config.mouseDownOnSelect = false;
//      input.focus();
//    }
//  });

	// mouseup on scrollbar does not fire in all browsers so install this event
	// handler to hide the select after a mouseup on the scrollbar
	$(document).mousedown(function() {
		config.mouseDownOnSelect = false;
		hideResultsNow('whole-word');
	});

// 	var blockSubmit;

	// prevent form submit in opera when selecting with return key
//   $.browser.opera && $(input.form).bind("submit.autocomplete", function() {
//     if (blockSubmit) {
//       blockSubmit = false;
//       return false;
//     }
//   });

	// helper function used for KEY.UP, ...
	var navigate = function(event, action) {
		// action should be a string

		event.preventDefault();
		if (select.visible())
			select[action]();
		// open result list if not visible
		else if (options.dropdown)
			open_complete_list();
		else
			onChange(0, true);

		// Set hasFocus to 1 if key was pressed cause then we are for sure
		// in the input field
		if (hasFocus <= 0)
			hasFocus = 1;
	};
	// only opera doesn't trigger keydown multiple times while pressed, others don't work with keypress at all
	$input.bind("keydown" + ".autocomplete", function(event) {
		// track last key pressed
		lastKeyPressCode = event.keyCode;
		switch(event.keyCode) {

			case KEY.UP:
				navigate(event, 'prev');
				break;

			case KEY.DOWN:
				navigate(event, 'next');
				break;

			case KEY.PAGEUP:
				navigate(event, 'pageUp');
				break;

			case KEY.PAGEDOWN:
				navigate(event, 'pageDown');
				break;

			// do not trigger search (onchange) when navigating
			// througth the input box
			case KEY.LEFT_ARROW:
			case KEY.RIGHT_ARROW:
			case KEY.HOME:
			case KEY.END:
				if (hasFocus <= 0)
					hasFocus = 1;
				break;

			// matches also semicolon
			case options.multiple && $.trim(options.multipleSeparator) == "," && KEY.COMMA:
			case KEY.TAB:
			case KEY.RETURN:
				if (hasFocus <= 0)
					hasFocus = 1;
				if( selectCurrent() ) {
					// stop default to prevent a form submit, Opera needs special handling
					event.preventDefault();
// 					blockSubmit = true;
					return false;
				}
				break;

			default:
				clearTimeout(timeout);
				// only add "long" delays for ajax requests, so use 10 ms here!
				timeout = setTimeout(function() { onChange(0, false); }, 10);

				if (hasFocus <= 0)
					hasFocus = 1;
				break;
		}
	}).focus(function() {
		// track whether the field has focus, we shouldn't process any
		// results if the field no longer has focus
		hasFocus++;
		// IE does fire focus when positioning the cursor, after selecting an
		// item from the result list we position the cursor manually at the
		// end but do not want to make another search request
		if (!config.from_selection) {
			if (options.dropdown) {
				// IE specific only open_up the complete list if list is not visible
				// if the result list was mousedowned and the user mouseups on document
				// ie gets a new focus which would open the complete list again but if
				// the input is not empty this would result in wrong behavior!
				if (!select.visible())
					open_complete_list();
				else
					$.Autocompleter.Selection(input, input.value.length, input.value.length);
			}
			else {
				onChange(0, false);
				// always position cursor at the end of the input field, autofill fills
				// the input so there is no need to put the cursor at the end
				if (!options.autoFill)
					$.Autocompleter.Selection(input, input.value.length, input.value.length);
			}
		}
		config.from_selection = false;
	}).blur(function(event) {
		hasFocus = 0;
		// set lastKeyPressCode to undefined in order to open the list on next focus
		// cause onChange checks lastKeyPressCode
		if (lastKeyPressCode == KEY.DEL || lastKeyPressCode == KEY.SHIFT
				|| lastKeyPressCode == KEY.BACKSPACE)
			lastKeyPressCode = undefined;

		if (!config.mouseDownOnSelect) {
			hideResults();
		}
	}).mousedown(function(event) {
		// prevent a mousedown being send to body and excecuting the handler installed on body
		// TODO: replace this function with the plugin which monkey patches jquery and adds an
		// event afterclick in order not to stop the propagation!
		event.stopPropagation();
		// TODO: should a mousedown open the result list again, if hasFocus?
	}).mouseup(function(event) {
		// do not undo autoFill
		if(options.autoFill && $input.val() && !previousValue) {
			event.preventDefault();
			// IE specific
			$(this).css('cursor', 'text');
		}
	}).bind("search", function() {
		// TODO why not just specifying both arguments?
		var fn = (arguments.length > 1) ? arguments[1] : null;
		function findValueCallback(q, data) {
			var result;
			if( data && data.length ) {
				for (var i=0; i < data.length; i++) {
					if( data[i].result.toLowerCase() == q.toLowerCase() ) {
						result = data[i];
						break;
					}
				}
			}
			if( typeof fn == "function" ) fn(result);
			else $input.trigger("result", result && [result.data, result.value]);
		}
		$.each((options.multiple) ? trimWords($input.val()) : [$input.val()],
				function(i, value) {
					request(value, findValueCallback, findValueCallback);
		});
	}).bind("flushCache", function() {
		cache.flush();
	}).bind("setOptions", function() {
		$.extend(options, arguments[1]);
		// if we've updated the data, repopulate
		if ( "data" in arguments[1] )
			cache.populate();
	}).bind("unautocomplete", function() {
		select.unbind();
		$input.unbind();
		$(input.form).unbind(".autocomplete");
	});

	function selectCurrent() {
		var selected = select.selected();
		if( !selected )
			return false;

		var v = selected.result;
		previousValue = v;

		if ( options.multiple ) {
			var words = trimWords($input.val());
			if ( words.length > 1 ) {
				v = words.slice(0, words.length - 1).join( options.multipleSeparator ) + options.multipleSeparator + v;
			}
			v += options.multipleSeparator;
		}

		$input.val(v);
		hideResultsNow('from-selected');
		$input.trigger("result", [selected.data, selected.value]);
		return true;
	}

	function onChange(crap, skipPrevCheck) {
		// do not show special result help when dropdown is set
		if (lastKeyPressCode == KEY.DEL && !options.dropdown) {
			// do not autoselect when autoFill is set
			if (!$input.val() && hasFocus)
				showSpecialResult('help_text');
			return;
		}

		if (lastKeyPressCode == KEY.SHIFT ||
				(lastKeyPressCode == KEY.BACKSPACE && !$input.val() && previousValue == ''))
			return;

		var currentValue = $input.val();
		// IE specific
		if (!skipPrevCheck && currentValue == previousValue && select.visible()) {
			if (!currentValue && !options.dropdown && hasFocus)
				showSpecialResult('help_text');
			return;
		}

		previousValue = currentValue;

		currentValue = lastWord(currentValue);
		if ( currentValue.length >= options.minChars) {
			$input.addClass(options.loadingClass);
			if (!options.matchCase)
				currentValue = currentValue.toLowerCase();
			request(currentValue, receiveData, hideResultsNow);
		} else {
			stopLoading();
			if (hasFocus)
				showSpecialResult('help_text');
		}
	}

	function trimWords(value) {
		if ( !value ) {
			return [""];
		}
		var words = value.split( options.multipleSeparator );
		var result = [];
		$.each(words, function(i, value) {
			if ( $.trim(value) )
				result[i] = $.trim(value);
		});
		return result;
	}

	function lastWord(value) {
		if ( !options.multiple )
			return value;
		var words = trimWords(value);
		return words[words.length - 1];
	}

	// fills in the input box w/the first match (assumed to be the best match)
	// q: the term entered
	// sValue: the first matching result
	function autoFill(q, sValue){
		// autofill in the complete box w/the first match as long as the user hasn't entered in more data
		// if the last user key pressed was backspace, don't autofill
		if( options.autoFill && (lastWord($input.val()).toLowerCase() == q.toLowerCase()) && lastKeyPressCode != KEY.BACKSPACE ) {
			// fill in the value (keep the case the user has typed)
			$input.val($input.val() + sValue.substring(lastWord(previousValue).length));
			// select the portion of the value not typed by the user (so the next character will erase)
			$.Autocompleter.Selection(input, previousValue.length, previousValue.length + sValue.length);
		}
	}

	function hideResults() {
		// only called from blur (for now) so pass whole-word with value true
		clearTimeout(timeout);
		// smaller delay in order to show help_text faster
		timeout = setTimeout(function() { hideResultsNow('whole-word'); }, 50);
	}

	function hideResultsNow(from) {
		if (options.dropdown)
			select.hide(true);
		else
			select.hide();
		clearTimeout(timeout);
		stopLoading();
		if (options.mustMatch) {
			if (from != 'from-selected')
				// call search and run callback
				$input.search(
					function (result) {
						// if no value found, remove last character to get to the last found
						// result or remove a whole-word if specified (for example onblur)
						if (!result) {
							if (from == 'whole-word') {
								if (options.multiple) {
									var words = trimWords($input.val()).slice(0, -1);
									$input.val( words.join(options.multipleSeparator) + (words.length ? options.multipleSeparator : "") );
								}
								else {
									$input.val("");
									previousValue = '';
								}
								// whole-word options only passed by bluring and the dropdown so do not
								// show 'no_results' if val == ''
							}
							else {
								var rolledback = false;
								var tmp_val = $input.val();
								var tmp_cache = null;
								if (tmp_val) {
									do {
										if (options.multiple)
											tmp_val = lastWord(tmp_val);
										tmp_cache = cache.load(
												(!options.matchCase) ? tmp_val.toLowerCase() : tmp_val);
										if (!(tmp_cache && tmp_cache.length)) {
											$input.val($input.val().slice(0, $input.val().length - 1));
											rolledback = true;
											tmp_val = $input.val();
										}
									} while(!(tmp_cache && tmp_cache.length) && tmp_val)
								}

								if (rolledback) {
									// do not cache previousValue otherwise onChange will return
									// without checking against the same value
									previousValue = previousValue.substr(0,previousValue.length-1);
									if (hasFocus) {
										if ($input.val() || options.minChars == 0) {
											if (!$input.val()) {
												// coming from options.minChars so show whole list
												tmp_cache = cache.load('');
											}
											select.display(tmp_cache, $input.val());
											select.show();
										}
										else if (!options.dropdown)
											showSpecialResult('no_results');
										else
											open_complete_list();
									}
								}
							}
						}
						else if (options.dropdown) {
							// put the exact result into the input
							// TODO: always put the excact value into the input?
							$input.val(result.result);
						}
					}
				);
		}
	}

	function receiveData(q, data) {
		if ( data && data.length && hasFocus ) {
			stopLoading();
			select.display(data, q);
			autoFill(q, data[0].result);

			// do not show the result list, if input has been removed
			if($('body', $input.parents()).get(0) && hasFocus)
				select.show();
		}
		// from ajax without results
		else {
			stopLoading();
			if (hasFocus)
				showSpecialResult('no_results');
			// run code to delete letters that are not correct! But remember:
			// This is bad user design cause the user first has to wait for
			// ajax do be completed and than suddenly characters disappear!
			if (options.mustMatch)
				hideResultsNow();
		}
	}

		var last_term = null;
	function request(term, success, failure) {
		if (!options.matchCase)
			term = term.toLowerCase();
		var data = cache.load(term);
		last_term = term;
		// recieve the cached data
		if (data && data.length) {
			success(term, data);
		// if an AJAX url has been supplied, try loading the data now
		} else if( (typeof options.url == "string") && (options.url.length > 0) ){
						var ajax_request = function() {
								var local_term = term;
								last_term = term;

								var extraParams = {
										timestamp: new Date()
								};
								$.each(options.extraParams, function(key, param) {
										extraParams[key] = typeof param == "function" ? param() : param;
								});
								// only show special result if hasFocus but make ajax request anyway because request
					// can be called from hideResultsNow with option.mustMatch so remove letters!
				if (hasFocus)
						showSpecialResult('loading');
							$.ajax({
								// try to leverage ajaxQueue plugin to abort previous requests
								mode: "abort",
								// limit abortion to this input
								port: "autocomplete" + input.name,
								dataType: options.dataType,
								url: options.url,
								data: $.extend({
									query: lastWord(term),
									limit: options.lengthPerCacheKey
								}, extraParams),
								success: function(data) {
									var parsed = options.parse && options.parse(data) || parse(data);
									cache.add(last_term, parsed);
									if (local_term == last_term)
										success(term, parsed);
								},
								error: function(data) {}
							});
			};

			// use a timeout for ajax requests in order not to submit every keydown
			// event
			clearTimeout(timeout);
			timeout = setTimeout(ajax_request, options.delay);
		}
		else {
			// if we have a failure, we need to empty the list -- this prevents the the [TAB] key from selecting the last successful match
			select.emptyList();
		 if (hasFocus)
				showSpecialResult('no_results');
		 if (options.mustMatch)
			 failure();
		}
	}

	function parse(data) {
		var parsed = [];
		var rows = data.split("\n");
		for (var i=0; i < rows.length; i++) {
			var row = $.trim(rows[i]);
			if (row) {
				row = row.split("|");
				parsed[parsed.length] = {
					data: row,
					value: row[0],
					result: options.formatResult && options.formatResult(row, row[0]) || row[0]
				};
			}
		}
		return parsed;
	}

	function stopLoading() {
		$input.removeClass(options.loadingClass);
	}

};

$.Autocompleter.defaults = {
	inputClass: "ac_input",
	resultsClass: "ac_results",
	loadingClass: "ac_loading",
	minChars: 1,
	delay: 400,
	matchCase: false,
	matchSubset: true,
	matchContains: true,
	cacheLength: 10,
	max: 100,
	mustMatch: false,
	extraParams: {},
	selectFirst: true,
	formatItem: function(row) { return row[0]; },
	formatMatch: null,
	autoFill: false,
	width: 0,
	multiple: false,
	multipleSeparator: ",",
	highlight: function(value, term) {
		// highlight all words in our results
		var words = $.trim(term).split(/\s+|-/g);
			for (var i = 0; i < words.length; i++) {
				if (words[i]) {
					value = value.replace(new RegExp("(?![^&;]+;)(?!<[^<>]*)(" + words[i].replace(/([\^\$\(\)\[\]\{\}\*\.\+\?\|\\])/gi, "\\$1") + ")(?![^<>]*>)(?![^&;]+;)", "gi"), "<strong>$1</strong>");
				}
			}
		return value;
	},
	dropdown: '',
	scroll: true,
	scrollHeight: 180,
	help_text: '<div class="help_text">Type to see suggestions</div>',
	no_results: '<div class="no_results">No results found</div>',
	loading: '<div class="loading"></div>'
};

$.Autocompleter.Cache = function(options) {
// example of how data is stored internally if used with ajax
// for example, the user searched for 'ind', 'naru', 'nine tai', then
// data will look like this:
//  data = {
//    'ind' : [{
//      'value': '<span>index your data by... </span>',
//      'result': 'index your data by...',
//      }, {
//      'value': '<span>users are used to index their... </span>',
//      'result': 'users are used to index their...',
//      }, ...],
//      'naru': [..., ...],
//      'nine tai': [..., ...]
//}
// chacheLength is the number of maximum KEYS in data not the number of
// max results to cache, for each key there can be a big number of results!
	var data = {};
	var length = 0;

	function matchSubset(s, sub) {
			// terms like 'search-index' should 'search' for search and 'index''!
			var words = $.trim(sub).split('-');
			for (var i = 0; i < words.length; i++) {
				if ($.trim(words[i])) {
					if (!options.matchCase)
						s = s.toLowerCase();
					// indexOf an empty string returns 0!
					var j = s.indexOf(sub);
					if (j == -1) return false;
					return j == 0 || options.matchContains;
				}
			}
		}

	function add(q, value) {
		// is the cache bigger then allowed?
		if (length > options.cacheLength){
			flush();
		}
		if (!data[q]){
			length++;
		}
		data[q] = value;
	}

	function populate(){
		if( !options.data ) return false;
		// track the matches
		var stMatchSets = {},
			nullData = 0;

		// no url was specified, we need to adjust the cache length to make sure it fits the local data store
		if( !options.url ) options.cacheLength = 1;

		// track all options for minChars = 0
		stMatchSets[""] = [];

		// loop through the array and create a lookup structure
		for ( var i = 0, ol = options.data.length; i < ol; i++ ) {
			var rawValue = options.data[i];
			// if rawValue is a string, make an array otherwise just reference the array
			rawValue = (typeof rawValue == "string") ? [rawValue] : rawValue;

			var value = options.formatMatch(rawValue, i+1, options.data.length);
			if ( value === false )
				continue;

			var firstChar = value.charAt(0).toLowerCase();
			// if no lookup array for this character exists, look it up now
			if( !stMatchSets[firstChar] )
				stMatchSets[firstChar] = [];

			// if the match is a string
			var row = {
				value: value,
				data: rawValue,
				result: options.formatResult && options.formatResult(rawValue) || value
			};

			// push the current match into the set list
			stMatchSets[firstChar].push(row);

			// keep track of  zero items
			if ( nullData++ < options.max ) {
				stMatchSets[""].push(row);
			}
		}

		// add the data items to the cache
		$.each(stMatchSets, function(i, value) {
			// increase the cache size
			options.cacheLength++;
			// add to the cache
			add(i, value);
		});
	}

	// populate any existing data
	setTimeout(populate, 25);

	function flush(){
		data = {};
		length = 0;
	}

	return {
		flush: flush,
		add: add,
		populate: populate,
		load: function(q) {
			if (!options.cacheLength || !length)
				return null;
			/*
			 * if dealing w/local data and matchContains than we must make sure
			 * to loop through all the data collections looking for matches
			 */
			if( !options.url && options.matchContains ){
				// track all matches
				var csub = [];
				// loop through all the data grids for matches
				for( var k in data ){
					// don't search through the stMatchSets[""] (minchars: 0) cache
					// this prevents duplicates
					if( k.length > 0 ){
						var c = data[k];
						$.each(c, function(i, x) {
							// if we've got a match, add it to the array
							if (matchSubset(x.value, q)) {
								csub.push(x);
							}
						});
					}
				}
				return csub;
			} else
			// if the exact item exists, use it
			if (data[q]){
				return data[q];
			} else
			if (options.matchSubset) {
				for (var i = q.length - 1; i >= options.minChars; i--) {
					var c = data[q.substr(0, i)];
					if (c) {
						var csub = [];
						$.each(c, function(i, x) {
							if (matchSubset(x.value, q)) {
								csub[csub.length] = x;
							}
						});
												// if the there are less results found make another
												// ajax request!
												if (csub.length < c.length
																&& !(c.length < options.lengthPerCacheKey)) {
														return null;
												}
						return csub;
					}
				}
			}
			return null;
		}
	};
};

$.Autocompleter.Select = function (options, input, select, config) {
	var CLASSES = {
		ACTIVE: "ac_over"
	};

	var listItems,
		active = -1,
		data,
		term = "",
		needsInit = true,
		element,
		list,
		types = ['loading', 'no_results', 'help_text'];

	function hover(event) {
		var tar = target(event);
		if(tar.nodeName && tar.nodeName.toUpperCase() == 'LI') {
			active = $('li', list).removeClass(CLASSES.ACTIVE).index(tar);
			$(tar).addClass(CLASSES.ACTIVE);
		}
	}

	function mousedown_handler(event) {
		config.mouseDownOnSelect = true;
		// IE specific
		setTimeout(function() { input.focus(); }, 50);
		return false;
	}

	// Create results
	function init() {
				active = -1;
		if (!needsInit)
			return;
		element = $("<div/>")
		.hide()
		.addClass(options.resultsClass)
		.css("position", "absolute")
		.appendTo(document.body);

		// TODO: define little api for new types
		// helper function
		var stoppropagation = function() {
			return false;
		};
		for (var i = 0; i < types.length; i++) {
			if (typeof options[types[i]] == 'string')
				options[types[i]] = $(options[types[i]]);
			options[types[i]].appendTo(element);
			options[types[i]].addClass('ac-special-result ' + types[i]);
			options[types[i]].mousedown(mousedown_handler).mouseup(function () {
				config.mouseDownOnSelect = false;
				// IE specific
				input.focus();
				return false;
			}).click(stoppropagation).bind('selectstart', stoppropagation).mousemove(
					function(event) {
							$(this).css('cursor', 'default');
			});
			options[types[i]].hide();
		}

		list = $("<ul/>").appendTo(element).mouseover(hover).mousedown(
				mousedown_handler).bind('selectstart', function() {
				// IE specific
				return false;
		}).mouseup(function(event) {
			config.mouseDownOnSelect = false;
			var tar = target(event);

			// we got a mouseup on the scroll
			// TODO: find a way to tell if scrollbar is visible
			if (!tar.nodeName && options.scroll) {
				input.focus();
				return false;
			}

			$(tar).addClass(CLASSES.ACTIVE);
			select();

			// IE does fire focus when positioning cursor but we do not
			// want to make another search request so set config.from_selection to
			// avoid a request
			config.from_selection = true;
			$.Autocompleter.Selection(input, input.value.length, input.value.length);

			// set it to false again for all other browsers!
			setTimeout(function() {
				config.from_selection = false;
			}, 200);

			// TODO: prevent from mouseup on body?
			return false;
		}).mouseleave(function(event) {
			if (options.selectFirst) {
				$("li", list).removeClass(CLASSES.ACTIVE);
				if (listItems)
					listItems.slice(0, 1).addClass(CLASSES.ACTIVE);
				active = 0;
			}
			else {
				$("li", list).removeClass(CLASSES.ACTIVE);
				active = -1;
			}
		});

		if( options.width > 0 )
			element.css("width", options.width);

		needsInit = false;
	}

	function target(event) {
		var element = event.target;
		while(element && element.tagName != "LI")
			element = element.parentNode;
		// more fun with IE, sometimes event.target is empty, just ignore it then
		if(!element)
			return [];
		return element;
	}

	function moveSelect(step) {
		if (listItems)
			listItems.slice(active, active + 1).removeClass(CLASSES.ACTIVE);
		else
			return;
		movePosition(step);
		var activeItem = listItems.slice(active, active + 1).addClass(CLASSES.ACTIVE);
		if(options.scroll) {
			var offset = 0;
			listItems.slice(0, active).each(function() {
				offset += this.offsetHeight;
			});
			if((offset + activeItem[0].offsetHeight - list.scrollTop()) > list[0].clientHeight) {
				list.scrollTop(offset + activeItem[0].offsetHeight - list.innerHeight());
			}
			else if(offset < list.scrollTop()) {
				list.scrollTop(offset);
			}
		}
	}

	function movePosition(step) {
		active += step;
		if (active < 0) {
			active = listItems.size() - 1;
		} else if (active >= listItems.size()) {
			active = 0;
		}
	}

	function limitNumberOfItems(available) {
		return options.max && options.max < available
			? options.max
			: available;
	}

	function fillList() {
		list.empty();
		var max = limitNumberOfItems(data.length);
		for (var i=0; i < max; i++) {
			if (!data[i])
				continue;
			var formatted = options.formatItem(data[i].data, i+1, max, data[i].value, term);
			if ( formatted === false )
				continue;
			// firefox has problems with mouseover on li elements in ul elements so
			// wrap the results into a div
			var div = $("<div/>").html(options.highlight(formatted, term));
			div.css('overflow', 'hidden');
			var li = $("<li/>").addClass(i%2 == 0 ? "ac_even" : "ac_odd").appendTo(list)[0];
			$(li).append(div);
			$.data(li, "ac_data", data[i]);
		}
		listItems = list.find("li");
		if ( options.selectFirst ) {
			listItems.slice(0, 1).addClass(CLASSES.ACTIVE);
			active = 0;
		}
		// apply bgiframe if available
		if ( $.fn.bgiframe )
			list.bgiframe();
	}

	// helper function to set the li to active on which the mouse moves after
	// a key has selected another one
	function unbind_mousemove (event) {
		hover(event);
		$(this).unbind('mousemove');
	}

	return {
		// init used for special results
		init: function() {
			init();
			list.empty();
		},
		display: function(d, q) {
			init();
			data = d;
			term = q;
			fillList();
		},
		next: function() {
			moveSelect(1);
			list.mousemove(unbind_mousemove);
		},
		prev: function() {
			moveSelect(-1);
			list.mousemove(unbind_mousemove);
		},
		pageUp: function() {
			if (active != 0 && active - 8 < 0) {
				moveSelect( -active );
			} else {
				moveSelect(-8);
			}
			list.mousemove(unbind_mousemove);
		},
		pageDown: function() {
			if (listItems && (active != listItems.size() - 1 && active + 8 > listItems.size())) {
				moveSelect( listItems.size() - 1 - active );
			} else {
				moveSelect(8);
			}
			list.mousemove(unbind_mousemove);
		},
		hide: function(remove_active) {
			if (options.dropdown)
				$(input).css({
					'background': 'white url(' + options.dropdown[0] + ') center right no-repeat'
				});
			$('.ac-special-result', element).hide();
			element && element.hide();
			if (!remove_active && listItems) {
				listItems.removeClass(CLASSES.ACTIVE);
				active = -1;
			}
		},
		visible : function() {
			return element && element.is(":visible");
		},
		current: function() {
			return this.visible() && (listItems && (listItems.filter("." + CLASSES.ACTIVE)[0] || options.selectFirst && listItems[0]));
		},
		show: function(type) {
            $('#advanced-search').hide();
			if (options.dropdown)
				$(input).css({
					'background': 'white url(' + options.dropdown[1] + ') center right no-repeat'
				});
			$('.ac-special-result', element).hide();

			if (type && typeof type == 'string') {
				options[type].show();
			}

			var offset = $(input).offset();
			element.css({
				width: typeof options.width == "string" || options.width > 0 ? options.width : $(input).width(),
				top: offset.top + input.offsetHeight,
				left: offset.left
			}).show();

			if(options.scroll) {
				list.scrollTop(0);
				list.css({
					maxHeight: options.scrollHeight,
					overflow: 'auto'
				});

				if(typeof document.body.style.maxHeight === "undefined") {
					var listHeight = 0;
					if (listItems)
						listItems.each(function() {
							listHeight += this.offsetHeight;
						});
					var scrollbarsVisible = listHeight > options.scrollHeight;
										list.css('height', scrollbarsVisible ? options.scrollHeight : listHeight );
					if (!scrollbarsVisible && listItems) {
						// IE doesn't recalculate width when scrollbar disappears
						listItems.width( list.width() - parseInt(listItems.css("padding-left")) - parseInt(listItems.css("padding-right")) );
					}
				}
			}
		},
		selected: function() {
			var selected = listItems && listItems.filter("." + CLASSES.ACTIVE).removeClass(CLASSES.ACTIVE);
			return selected && selected.length && $.data(selected[0], "ac_data");
		},
		emptyList: function (){
			list && list.empty();
			// list.append();
		},
		unbind: function() {
			element && element.remove();
		}
	};
};

$.Autocompleter.Selection = function(field, start, end) {
	if( field.createTextRange ){
		var selRange = field.createTextRange();
		selRange.collapse(true);
		selRange.moveStart("character", start);
		selRange.moveEnd("character", end);
		selRange.select();
	} else if( field.setSelectionRange ){
		field.setSelectionRange(start, end);
	} else {
		if( field.selectionStart ){
			field.selectionStart = start;
			field.selectionEnd = end;
		}
	}
	// needed for autoFill!
	field.focus();
};

})(jQuery);
