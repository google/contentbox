/*
 * This allows to create search forms whose results can be opened in a new tab.
 * Forms must be of class "search-form" to be handled by this script. All links
 * (a-tags) of class "submit-link" within the form are made "submit"-links.
 */

(function($) {

var getlink = function(form) {
  var base_url = form.action + (form.action.indexOf('?') >= 0 ? '&' : '?');
  data = $(form).formSerialize();
  return data ? base_url + data : form.action;
};

$('form.search-form').livequery(function() {
  var form = this;
  $(this).find('a.submit-link').each(function() {
    $(this).focus(function() {
      $(this).attr('href', getlink(form));
    });
    $(this).hover(function() {
      $(this).attr('href', getlink(form));
    }, function() {});
  });
  $(this).submit(function() {
    document.location.href = getlink(form);
    return false;
  });
});

})(jQuery);
