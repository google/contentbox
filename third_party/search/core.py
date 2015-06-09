from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import signals
from djangotoolbox.fields import ListField
from djangotoolbox.utils import getattr_by_path
from copy import deepcopy
import re
import string

_PUNCTUATION_REGEX = re.compile(
    '[' + re.escape(string.punctuation.replace('-', '').replace(
        '_', '').replace('#', '')) + ']')
_PUNCTUATION_SEARCH_REGEX = re.compile(
    '[' + re.escape(string.punctuation.replace('_', '').replace(
        '#', '')) + ']')

# Various base indexers
def startswith(words, indexing, **kwargs):
    """Allows for word prefix search."""
    if not indexing:
        # In search mode we simply match search terms exactly
        return words
    # In indexing mode we add all prefixes ('h', 'he', ..., 'hello')
    result = []
    for word in words:
        result.extend([word[:count].strip(u'-')
                       for count in range(1, len(word)+1)])
    return result

def porter_stemmer(words, language, **kwargs):
    """Porter-stemmer in various languages."""
    languages = [language,]
    if '-' in language:
        languages.append(language.split('-')[0])

    # Fall back to English
    languages.append('en')

    # Find a stemmer for this language
    for language in languages:
        try:
            stem = __import__('search.porter_stemmers.%s' % language,
                                 {}, {}, ['']).stem
        except:
            continue
        break

    result = []
    for word in words:
        result.append(stem(word))
    return result

stop_words = {
    'en': set(('a', 'an', 'and', 'or', 'the', 'these', 'those', 'whose', 'to')),
    'de': set(('ein', 'eine', 'eines', 'einer', 'einem', 'einen', 'den',
               'der', 'die', 'das', 'dieser', 'dieses', 'diese', 'diesen',
               'deren', 'und', 'oder'))
}

def get_stop_words(language):
    if language not in stop_words and '-' in language:
        language = language.split('-', 1)[0]
    return stop_words.get(language, set())

def non_stop(words, indexing, language, **kwargs):
    """Removes stop words from search query."""
    if indexing:
        return words
    return list(set(words) - get_stop_words(language))

def porter_stemmer_non_stop(words, **kwargs):
    """Combines porter_stemmer with non_stop."""
    return porter_stemmer(non_stop(words, **kwargs), **kwargs)

# Language handler
def site_language(instance, **kwargs):
    """The default language handler tries to determine the language from
    fields in the model instance."""

    # Check if there's a language attribute
    if hasattr(instance, 'language'):
        return instance.language
    if hasattr(instance, 'lang'):
        return instance.lang

    # Fall back to default language
    return settings.LANGUAGE_CODE

def default_splitter(text, indexing=False, **kwargs):
    """
    Returns an array of  keywords, that are included
    in query. All character besides of letters, numbers
    and '_' are split characters. The character '-' is a special
    case: two words separated by '-' create an additional keyword
    consisting of both words without separation (see example).

    Examples:
    - text='word1/word2 word3'
      returns ['word1', 'word2', word3]
    - text='word1/word2-word3'
      returns ['word1', 'word2', 'word3', 'word2word3']
    """
    if not text:
        return []
    if not indexing:
        return _PUNCTUATION_SEARCH_REGEX.sub(u' ', text.lower()).split()
    keywords = []
    for word in set(_PUNCTUATION_REGEX.sub(u' ', text.lower()).split()):
        if not word:
            continue
        if '-' not in word:
            keywords.append(word)
        else:
            keywords.extend(get_word_combinations(word))
    return keywords

def get_word_combinations(word):
    """
    'one-two-three'
    =>
    ['one', 'two', 'three', 'onetwo', 'twothree', 'onetwothree']
    """
    permutations = []
    parts = [part for part in word.split(u'-') if part]
    for count in range(1, len(parts) + 1):
        for index in range(len(parts) - count + 1):
            permutations.append(u''.join(parts[index:index+count]))
    return permutations

class DictEmu(object):
    def __init__(self, data):
        self.data = data
    def __getitem__(self, key):
        return getattr(self.data, key)

# IndexField is a (String)ListField storing indexed fields of a model_instance
class IndexField(ListField):
    def __init__(self, search_manager, *args, **kwargs):
        self.search_manager = search_manager
        kwargs['item_field'] = models.CharField(max_length=500)
        kwargs['editable'] = False
        super(IndexField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if self.search_manager.filters and not \
                self.search_manager.should_index(DictEmu(model_instance)):
            return []

        language = self.search_manager.language
        if callable(language):
            language = language(model_instance, property=self)

        index = []
        for field_name in self.search_manager.fields_to_index:
            values = getattr_by_path(model_instance, field_name, None)
            if not values:
                values = ()
            elif not isinstance(values, (list, tuple)):
                values = (values,)
            for value in values:
                index.extend(self.search_manager.splitter(value, indexing=True,
                    language=language))
        if self.search_manager.indexer:
            index = self.search_manager.indexer(index, indexing=True,
                language=language)
        # Sort index to make debugging easier
        setattr(model_instance, self.search_manager.search_list_field_name,
            sorted(set(index)))
        return index

class SearchManager(models.Manager):
    """
    Simple full-text manager adding a search function.

    If "relation_index" is True the index will be stored in a separate entity.

    With "integrate" you can add fields to your relation index,
    so they can be searched, too.

    With "filters" you can specify when a values index should be created.
    """
    def __init__(self, fields_to_index, indexer=None, splitter=default_splitter,
            relation_index=True, integrate='*', filters={},
            language=site_language, **kwargs):
        # integrate should be specified when using the relation index otherwise
        # we doublicate the amount of data in the datastore and the relation
        # index makes no sense any more
        # TODO: filters has to be extended (maybe a function) to allow Django's
        # QuerySet methods like exclude
        if integrate is None:
            integrate = ()
        if integrate == '*' and not relation_index:
            integrate = ()
        if isinstance(fields_to_index, basestring):
            fields_to_index = (fields_to_index,)
        self.fields_to_index = fields_to_index
        if isinstance(integrate, basestring):
            integrate = (integrate,)
        self.filters = filters
        self.integrate = integrate
        self.splitter = splitter
        self.indexer = indexer
        self.language = language
        self.relation_index = relation_index
        if len(fields_to_index) == 0:
            raise ValueError('No fields specified for index!')
        # search_list_field_name will be set if no relation_index is used that is
        # for relation_index=False or for the relation_index_model itself
        self.search_list_field_name = ''
        super(SearchManager, self).__init__(**kwargs)

    def contribute_to_class(self, model, name):
        super(SearchManager, self).contribute_to_class(model, name)
        # set default_manager to None such that the default_manager will be set
        # to 'objects' via the class-prepared signal calling
        # ensure_default_manager
#        setattr(model, '_default_manager', None)
        self.name = name
        # add IndexField to the model if we do not use the relation_index
        if not self.relation_index:
            self.search_list_field_name = "%s_search_list_field" %name
            # Add field to class dynamically
            setattr(model, self.search_list_field_name, IndexField(self))
            getattr(model, self.search_list_field_name).contribute_to_class(
                model, self.search_list_field_name)

    def filter(self, values):
        """
        Returns a query for the given values (creates '=' filters for the
        IndexField. Additionally filters can be applied afterwoods via chaining.
        """
        if not isinstance(values, (tuple, list)):
            values = (values,)
        filtered = self.model.objects.all()
        for value in set(values):
            filter = {self.search_list_field_name:value}
            filtered = filtered.filter(**filter)
        return filtered

    def _search(self, query, indexer=None, splitter=None,
            language=settings.LANGUAGE_CODE):
        if not splitter:
            splitter = default_splitter
        words = splitter(query, indexing=False, language=language)
        if indexer:
            words = indexer(words, indexing=False, language=language)
        # Optimize query
        words = set(words)
        if len(words) >= 4:
            words -= get_stop_words(language)
        # Don't allow empty queries
        if not words and query:
            # This query will never find anything
            return self.filter(()).filter({self.search_list_field_name:' '})
        return self.filter(sorted(words))

    def should_index(self, values):
        # Check if filter doesn't match
        if not values:
            return False
        for filter, value in self.filters.items():
            attr, op = filter, 'exact'
            if '__' in filter:
                attr, op = filter.rsplit('__', 1)
            op = op.lower()
            if (op == 'exact' and values[attr] != value or
#                    op == '!=' and values[attr] == value or
                    op == 'in' and values[attr] not in value or
                    op == 'lt' and values[attr] >= value or
                    op == 'lte' and values[attr] > value or
                    op == 'gt' and values[attr] <= value or
                    op == 'gte' and values[attr] < value):
                return False
            elif op not in ('exact', 'in', 'lt', 'lte', 'gte', 'gt'):
                raise ValueError('Invalid search index filter: %s %s' % (filter, value))
        return True

#    @commit_locked
    def update_relation_index(self, parent_pk, delete=False):
        relation_index_model = self._relation_index_model
        try:
            index = relation_index_model.objects.get(pk=parent_pk)
        except ObjectDoesNotExist:
            index = None

        if not delete:
            try:
                parent = self.model.objects.get(pk=parent_pk)
            except ObjectDoesNotExist:
                parent = None

            values = None
            if parent:
                values = self.get_index_values(parent)

        # Remove index if it's not needed, anymore
        if delete or not self.should_index(values):
            if index:
                index.delete()
            return

        # Update/create index
        if not index:
            index = relation_index_model(pk=parent_pk, **values)

        # This guarantees that we also set virtual @properties
        for key, value in values.items():
            setattr(index, key, value)

        index.save()

    def create_index_model(self):
        attrs = dict(__module__=self.__module__)
        # By default we integrate everything when using relation index
        # manager will add the IndexField to the relation index automaticaly
        if self.integrate == ('*',):
            self.integrate = tuple(field.name
                                   for field in self.model._meta.fields
                                   if not isinstance(field, IndexField))

        for field_name in self.integrate:
            field = self.model._meta.get_field_by_name(field_name)[0]
            field = deepcopy(field)
            attrs[field_name] = field
            if isinstance(field, models.ForeignKey):
                attrs[field_name].rel.related_name = '_sidx_%s_%s_%s_set_' % (
                    self.model._meta.object_name.lower(),
                    self.name, field_name,
                )

        owner = self
        def __init__(self, *args, **kwargs):
            # Save some space: don't copy the whole indexed text into the
            # relation index field unless the field gets integrated.
            field_names = [field.name for field in self._meta.fields]
            owner_field_names = [field.name
                                 for field in owner.model._meta.fields]
            for key, value in kwargs.items():
                if key in field_names or key not in owner_field_names:
                    continue
                setattr(self, key, value)
                del kwargs[key]
            models.Model.__init__(self, *args, **kwargs)
        attrs['__init__'] = __init__

        self._relation_index_model = type(
            ('RelationIndex_%s_%s_%s' % (self.model._meta.app_label,
                                        self.model._meta.object_name,
                                        self.name)).encode('ascii','ignore'),
            (models.Model,), attrs)
        self._relation_index_model.add_to_class(self.name, SearchManager(
            self.fields_to_index, splitter=self.splitter, indexer=self.indexer,
            language=self.language, relation_index=False))

    def get_index_values(self, parent):
        filters = []
        for filter in self.filters.keys():
            if '__' in filter:
                filters.append(filter.rsplit('__')[0])
            else:
                filters.append(filter)
        filters = tuple(filters)
        values = {}
        for field_name in set(self.fields_to_index + self.integrate + filters):
            field = self.model._meta.get_field_by_name(field_name)[0]
            if isinstance(field, models.ForeignKey):
                value = field.pre_save(parent, False)
            else:
                value = getattr(parent, field_name)
            if field_name == self.fields_to_index[0] and \
                    isinstance(value, (list, tuple)):
                value = sorted(value)
            if isinstance(field, models.ForeignKey):
                values[field.column] = value
            else:
                values[field_name] = value
        return values

    def search(self, query, language=settings.LANGUAGE_CODE):
        if self.relation_index:
            items = getattr(self._relation_index_model, self.name).search(query,
                language=language).values('pk')
            return RelationIndexQuery(self.model, items)
        return self._search(query, splitter=self.splitter,
            indexer=self.indexer, language=language)

def load_backend():
    backend = getattr(settings, 'SEARCH_BACKEND', 'search.backends.immediate_update')
    import_list = []
    if '.' in backend:
        import_list = [backend.rsplit('.', 1)[1]]
    return __import__(backend, globals(), locals(), import_list)

def post(delete, sender, instance, **kwargs):
    for counter, manager_name, manager in sender._meta.concrete_managers:
        if isinstance(manager, SearchManager):
            if manager.relation_index:
                backend = load_backend()
                backend.update_relation_index(manager, instance.pk, delete)

def post_save(sender, instance, **kwargs):
    post(False, sender, instance, **kwargs)

def post_delete(sender, instance, **kwargs):
    post(True, sender, instance, **kwargs)

def install_index_model(sender, **kwargs):
    needs_relation_index = False
    # what to do for abstract_managers?
    for counter, manager_name, manager in sender._meta.concrete_managers:
        if isinstance(manager, SearchManager) and manager.relation_index:
            manager.create_index_model()
            needs_relation_index = True
    if needs_relation_index:
        signals.post_save.connect(post_save, sender=sender)
        signals.post_delete.connect(post_delete, sender=sender)
#signals.class_prepared.connect(install_index_model)

class QueryTraits(object):
    def __iter__(self):
        return iter(self[:301])

    def __len__(self):
        return self.count()

    def get(self, *args, **kwargs):
        result = self[:1]
        if result:
            return result[0]
        raise ObjectDoesNotExist

class RelationIndexQuery(QueryTraits):
    """Combines the results of multiple queries by appending the queries in the
    given order."""
    def __init__(self, model, query):
        self.model = model
        self.query = query

    def order_by(self, *args, **kwargs):
        self.query = self.query.order_by(*args, **kwargs)
        return self

    def filter(self, *args, **kwargs):
        self.query = self.query.filter(*args, **kwargs)
        return self

    def __getitem__(self, index):
        pks_slice = index
        if not isinstance(index, slice):
            pks_slice = slice(None, index + 1, None)

        pks = [instance.pk if isinstance(instance, models.Model) else instance['pk']
                for instance in self.query[pks_slice]]
        if not isinstance(index, slice):
            return self.model.objects.filter(pk__in=pks)[index]
        return self.model.objects.filter(pk__in=pks)[pks_slice]
#        return [item for item in self.model.objects.filter(
#            pk__in=pks) if item]


    def count(self):
        return self.query.count()

    # TODO: add keys_only query
#    def values(self, fields):
#        pass

def search(model, query, language=settings.LANGUAGE_CODE,
        search_index='search_index'):
    return getattr(model, search_index).search(query, language)