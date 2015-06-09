from django.conf import settings
from djangotoolbox.http import JSONResponse

def live_search_results(request, model, search_index='search_index', limit=30,
        result_item_formatting=None, query_converter=None,
        converter=None, redirect=False):
    """
    Performs a search in searched_model and prints the results as
    text, so it can be used by auto-complete scripts.

    limit indicates the number of results to be returned.

    A JSON file is sent to the browser. It contains a list of
    objects that are created by the function indicated by
    the parameter result_item_formatting. It is executed for every result
    item.
    Example:
    result_item_formatting=lambda course: {
        'value': course.name + '<br />Prof: ' + course.prof.name,
        'result': course.name + ' ' + course.prof.name,
        'data': redirect=='redirect' and
            {'link': course.get_absolute_url()} or {},
    }
    """
    query = request.GET.get('query', '')
    try:
        limit_override = int(request.GET.get('limit', limit))
        if limit_override < limit:
            limit = limit_override
    except:
        pass
    search_index = getattr(model, search_index)
    language = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
    results = search_index.search(query, language=language)
    if query_converter:
        results = query_converter(request, results)
    results = results[:limit]
    if converter:
        results = converter(results)
    data = []
    for item in results:
        if result_item_formatting:
            entry = result_item_formatting(item)
        else:
            value = getattr(item, search_index.fields_to_index[0])
            entry = {'value': force_escape(value), 'result': value}
        if 'data' not in entry:
            entry['data'] = {}
        if redirect:
            if 'link' not in entry['data']:
                entry['data']['link'] = item.get_absolute_url()
        data.append(entry)
    return JSONResponse(data)