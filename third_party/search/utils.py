
import logging
from django.conf import settings
from search.core import search, default_splitter, get_stop_words


def partial_match_search(model, query, query_filter_args=None, primary_rank_by_number_of_matches=True, ranking_field=None,
                         ranking_field_descending=True, exact_match_field=None, exact_match_min_keywords=2, blacklisted_keywords=[],
                         per_query_limit=40, debug=False, search_index='search_index', splitter=default_splitter,
                         language=settings.LANGUAGE_CODE, final_result_limit=None):
    """ 
    Args & Description:
    
    Uses nonrel-search (which is normally an AND search) to perform separate queries for each keyword and combine the 
    results. The result is an OR search where AND matches appear at the top. 
    
    If primary_rank_by_number_of_matches is True, the results will first be ranked by the number of keywords they 
    match and then by their desc_ranking_field. Otherwise, they will just be ranked by ranking_field. If ranking_field
    is None, that part of the ranking will be skipped. ranking_field_descending determines whether or not the ranking
    sort is applied in descending order.
    
    If exact_match_field is set, any results matching all query keywords in the given field (in any order) will be 
    returned as the only results. exact_match_min_keywords can be used to tune when this rule is applied.
    
    blacklisted_keywords in the query are ignored.
    
    Because of backend limitations, this partial match search is implemented using multiple queries (one for the 
    entire query, and one for each keyword). The per_query_limit limits the number of results that are fetched for 
    each of these queries and therefore also effects the number of final (deduplicated) results that are returned. 
    query_filter_args can be set to filter each of these these queries and thereby restrict the final results.
    
    Setting debug=True will print some info logs as the search results are queried and sorted.
    
    Return:
    
    Pre-sliced list of objects (not filterable).
    
    Simple example:
    results = partial_match_search(Indexed, 'foo bar', search_index='test_index')

    Production example:
    search_query_string = 'tech news'
    query_filter_args['is_deleted'] = False
    catalog_items = partial_match_search(CatalogItem, search_query_string, query_filter_args=query_filter_args,
                                         ranking_field='search_rank', ranking_field_descending=True, 
                                         exact_match_field='title', blacklisted_keywords=['com'])
    
    """

    try:
        keywords = get_keyword_set(query, blacklisted_keywords, splitter, language, debug)
        if debug:
            logging.info("search keywords: " + (', ').join(keywords))

        query_result_list = []

        query_set = search(model, query, language, search_index)
        if query_filter_args:
            query_set = query_set.filter(**query_filter_args)
        if ranking_field:
            query_set = query_set.order_by('-' + ranking_field)
            query_results = query_set[:per_query_limit]
            query_result_list.extend(query_results)

        for keyword in keywords:
            query_set = search(model, keyword, language, search_index)
            if query_filter_args:
                query_set = query_set.filter(**query_filter_args)
            if ranking_field:
                order_by = ranking_field
                if ranking_field_descending:
                    order_by = '-' + ranking_field
                query_set = query_set.order_by(order_by)
            query_results = query_set[:per_query_limit]
            if debug:
                logging.info("Result for of query for '" + repr(keyword) + "': " + repr(query_results) )
            query_result_list.extend(query_results)

        if debug:
            logging.info("Deduplicate and create primary search ranking based on how many keywords matched.")
        query_result_set = {}
        dedup_query_result_list = []
        all_keyword_match_dedup_query_result_list = []
        all_keyword_match = False
        for result in query_result_list:
            if exact_match_field and exact_match_min_keywords != None:

                all_keyword_match = False
                if len(keywords) >= exact_match_min_keywords:
                    all_keyword_match = True
                    exact_match_field_keywords = get_keyword_set(getattr(result, exact_match_field),
                            blacklisted_keywords, splitter, language, debug)
                    if len(keywords - exact_match_field_keywords) > 0:
                        all_keyword_match = False
            if result._get_pk_val() in query_result_set:
                query_result_set[result._get_pk_val()].__partial_match_search__primary_rank += 1
                if debug:
                    logging.info("number " + repr(query_result_set[result._get_pk_val()].__partial_match_search__primary_rank) +
                                 " instance of result: " + repr(result))
            else:
                if debug:
                    logging.info("first instance of result: " + repr(result))
                query_result_set[result._get_pk_val()] = result
                setattr(query_result_set[result._get_pk_val()], '__partial_match_search__primary_rank', 1)
                dedup_query_result_list.append(result)
                if all_keyword_match:
                    all_keyword_match_dedup_query_result_list.append(result)

        if len(all_keyword_match_dedup_query_result_list) > 0:
            if debug:
                logging.info("All keywords matched at least one result exact_match_field.  Using only these matches: " +
                             repr(len(all_keyword_match_dedup_query_result_list)))
            dedup_query_result_list = all_keyword_match_dedup_query_result_list
        else:
            if debug:
                logging.info("Found " + repr(len(dedup_query_result_list)) + " results.")

        if ranking_field:
            if ranking_field_descending:
                sorted_ranked_query_result_set = sorted(dedup_query_result_list, 
                                                        key=lambda result: (result.__partial_match_search__primary_rank,
                                                        getattr(result, ranking_field)), reverse=True)
            else:
                sorted_ranked_query_result_set = sorted(dedup_query_result_list, 
                                                        key=lambda result: (-result.__partial_match_search__primary_rank,
                                                        getattr(result, ranking_field)))
        else:
            sorted_ranked_query_result_set = sorted(dedup_query_result_list, 
                                                        key=lambda result: -result.__partial_match_search__primary_rank)

        if final_result_limit:
            sorted_ranked_query_result_set = sorted_ranked_query_result_set[:final_result_limit]

        if debug:
            logging.info('final result ordering:')
            for result in sorted_ranked_query_result_set:
                if ranking_field:
                    logging.info("primary_rank: " + repr(result.__partial_match_search__primary_rank) + ", ranking_field: " +
                             repr(getattr(result, ranking_field)) + ", result: " + repr(result))
                else:
                    logging.info("primary_rank: " + repr(result.__partial_match_search__primary_rank) + ", result: " + repr(result))

        return sorted_ranked_query_result_set
    except:
        logging.exception("Error in partial_match_search")
        return None


def get_keyword_set(query, blacklisted_keywords=[], splitter=default_splitter, language=settings.LANGUAGE_CODE,
                    debug=False):
    keywords = splitter(query, indexing=False, language=language)

    keywords = set(keywords)
    if len(keywords) >= 4:
        keywords -= get_stop_words(language)

    keywords -= set(blacklisted_keywords)
    return keywords


def comma_splitter(text, indexing=False, **kwargs):
    """ Comma delimited list splitter"""

    if not text:
        return []

    keywords = []
    for word in set(text.split(',')):
        if not word:
            continue
        else:
            keywords.append(word.strip().lower())

    return keywords
