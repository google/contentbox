from search.core import default_splitter, site_language, SearchManager, \
    install_index_model
from autoload import autodiscover as auto_discover

def autodiscover():
    auto_discover('search_indexes')

def register(model, fields_to_index, search_index='search_index',
    indexer=None, splitter=default_splitter, relation_index=True, integrate='*',
    filters={}, language=site_language, **kwargs):

    """
    Add a search manager to the model.
    """

    if not hasattr(model, '_meta'):
        raise AttributeError('The model being registered must derive from Model.')

    if hasattr(model, search_index):
        raise AttributeError('The model being registered already defines a'
            ' property called %s.' % search_index)

    model.add_to_class(search_index, SearchManager(fields_to_index, indexer,
        splitter, relation_index, integrate, filters, language, **kwargs))

    install_index_model(model)
