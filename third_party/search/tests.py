# -*- coding: utf-8 -*-
from django.db import models
from django.test import TestCase

# use immediate_update on tests
from django.conf import settings
settings.SEARCH_BACKEND = 'search.backends.immediate_update'

from search import register
from search.core import SearchManager, startswith
from search.utils import partial_match_search


# ExtraData is used for ForeignKey tests
class ExtraData(models.Model):
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)

    def __unicode__(self):
        return self.name

class Indexed(models.Model):
    extra_data = models.ForeignKey(ExtraData, related_name='indexed_model', null=True)
    extra_data2 = models.ForeignKey(ExtraData, null=True)

    # Test normal and prefix index
    one = models.CharField(max_length=500, null=True)
    two = models.CharField(max_length=500)
    check = models.BooleanField()
    value = models.CharField(max_length=500)
    
    def __unicode__(self):
        return ':'.join((repr(self.one), repr(self.two), repr(self.check), repr(self.value)))

register(Indexed, 'one', search_index='one_index', indexer=startswith)
register(Indexed, ('one', 'two'), search_index='one_two_index')
register(Indexed, 'value', integrate=('one', 'check'), search_index='value_index')

# Test filters
class FiltersIndexed(models.Model):
    value = models.CharField(max_length=500)
    check = models.BooleanField()

register(FiltersIndexed, 'value', filters={'check':True, }, search_index='checked_index')

class TestIndexed(TestCase):
    def setUp(self):
        extra_data = ExtraData()
        extra_data.save()

        Indexed(one=u'foo', two='bar').save()
        Indexed(one=u'foo_2', two='bar').save()

        for i in range(3):
            Indexed(extra_data=extra_data, one=u'OneOne%d' % i).save()

        for i in range(3):
            Indexed(extra_data=extra_data, one=u'one%d' % i, two='two%d' % i).save()

        for i in range(3):
            Indexed(extra_data=extra_data, one=(None, u'ÃœÃ„Ã–-+!#><|', 'blub')[i],
                    check=bool(i%2), value=u'value%d test-word' % i).save()

        for i in range(3):
            FiltersIndexed(check=bool(i%2), value=u'value%d test-word' % i).save()

    def test_setup(self):
        self.assertEqual(1, len(Indexed.one_two_index.search('foo bar')))

        self.assertEqual(len(Indexed.one_index.search('oneo')), 3)
        self.assertEqual(len(Indexed.one_index.search('one')), 6)

        self.assertEqual(len(Indexed.one_two_index.search('one2')), 1)
        self.assertEqual(len(Indexed.one_two_index.search('two')), 0)
        self.assertEqual(len(Indexed.one_two_index.search('two1')), 1)

        self.assertEqual(len(Indexed.value_index.search('word')), 3)
        self.assertEqual(len(Indexed.value_index.search('test-word')), 3)

        self.assertEqual(len(Indexed.value_index.search('value0').filter(
            check=False)), 1)
        self.assertEqual(len(Indexed.value_index.search('value1').filter(
            check=True, one=u'ÃœÃ„Ã–-+!#><|')), 1)
        self.assertEqual(len(Indexed.value_index.search('value2').filter(
            check__exact=False, one='blub')), 1)

        # test filters
        self.assertEqual(len(FiltersIndexed.checked_index.search('test-word')), 1)
        self.assertEqual(len(Indexed.value_index.search('foobar')), 0)

    def test_change(self):
        one = Indexed.one_index.search('oNeone1').get()
        one.one = 'oneoneone'
        one.save()

        value = Indexed.value_index.search('value0').get()
        value.value = 'value1 test-word'
        value.save()
        value.one = 'shidori'
        value.value = 'value3 rasengan/shidori'
        value.save()
        self.assertEqual(len(Indexed.value_index.search('rasengan')), 1)
        self.assertEqual(len(Indexed.value_index.search('value3')), 1)

        value = Indexed.value_index.search('value3').get()
        value.delete()
        self.assertEqual(len(Indexed.value_index.search('value3')), 0)

    def test_partial_match_search(self):
        import logging
        results = partial_match_search(Indexed, 'bar',\
                                       search_index='one_two_index')
        self.assertEqual(len(results), 2)
        
        results = partial_match_search(Indexed, 'foo',\
                                       search_index='one_two_index')
        self.assertEqual(len(results), 1)
        
        results = partial_match_search(Indexed, 'foo bar',\
                                       search_index='one_two_index')
        self.assertEqual(len(results), 2)

        results = partial_match_search(Indexed, 'one',\
                                       search_index='one_index')
        self.assertEqual(len(results), 6)
        
        results = partial_match_search(Indexed, 'one0 one1 one2',\
                                       search_index='one_index')
        self.assertEqual(len(results), 3)
        
        results = partial_match_search(Indexed, 'one one0 one1 one2',\
                                       search_index='one_index')
        self.assertEqual(len(results), 6)
        self.assertEqual(repr(results[0]), "<Indexed: u'one0':u'two0':False:u''>")
        self.assertEqual(repr(results[5]), "<Indexed: u'OneOne2':u'':False:u''>")


