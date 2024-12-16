from django.shortcuts import render
from django.http import JsonResponse
from products.documents import ProductDocument
from elasticsearch_dsl.query import MultiMatch, Fuzziness, Q
from elasticsearch_dsl import Search

def search_product(request):
    data = {
        "status": 200,
        "message": "Products",
        "products": []
    }

    if request.GET.get('search'):
        search = request.GET.get('search').split(',')
        
        query = MultiMatch(
            query=" ".join(search),
            fields=["title", "description"],
            fuzziness=Fuzziness.AUTO,
        )
        
        result = ProductDocument.search().query(query)
        result = result.sort('-price')
        result = result.extra(from_=1, size=3)
        
        result = result.execute()

        products = [
            {
                "title": hit.title,
                "description": hit.description,
                "category": hit.category,
                "price": hit.price,
                "brand": hit.brand,
                "sku": hit.sku,
                "thumbnail": hit.thumbnail,
                "score": hit.meta.score,
            }
            for hit in result
        ]
        
        data['products'] = products

    return JsonResponse(data)


def search_medium_product(request):
  
    data = {
        "status": 200,
        "message": "Products",
        "products": []
    }
    
    search = request.GET.get('search')
    category = request.GET.get('category')
    price_range = request.GET.get('price_range')
    tag = request.GET.get('tag')
    from_size = int(request.GET.get('from', 0)) 
    size = int(request.GET.get('size', 10))  

    query = Q("match_all") 

    # 1. Match Query (full-text search)
    if search:
        query = Q("match", title=search)
    
    # 2. Match Phrase Query (exact sequence match)
    if search and 'phrase' in request.GET:
        query = Q("match_phrase", title=search)
    
    # 3. Term Query (exact match)
    if 'term' in request.GET:
        query = Q("term", category=category)
    
    # 4. Terms Query (multiple values)
    if 'terms' in request.GET:
        terms = request.GET.get('terms').split(',')
        query = Q("terms", category=terms)
    
    # 5. Range Query
    if price_range:
        price_from, price_to = price_range.split(',')
        query &= Q("range", price={"gte": price_from, "lte": price_to})
    
    # 6. Boolean Query (must, should, must_not)
    bool_query = Q("bool", must=[Q("match", title=search)]) if search else Q("bool")
    if 'should' in request.GET:
        bool_query &= Q("should", match={"category": category})
    if 'must_not' in request.GET:
        bool_query &= Q("must_not", match={"brand": "SomeBrand"})
    query &= bool_query
    
    # 7. Nested Query
    if 'nested' in request.GET:
        query &= Q("nested", path="tags", query=Q("match", tags__tag="electronics"))
    
    # 8. Prefix Query
    if 'prefix' in request.GET:
        query &= Q("prefix", title="el")
    
    # 9. Wildcard Query
    if 'wildcard' in request.GET:
        query &= Q("wildcard", title="el*")
    
    # 10. Fuzzy Query
    if 'fuzzy' in request.GET:
        query &= Q("fuzzy", title={"value": search, "fuzziness": "AUTO"})
    
    # 11. Match All Query (default for no specific search)
    if 'match_all' in request.GET:
        query &= Q("match_all")
    
    # 12. Exists Query
    if 'exists' in request.GET:
        query &= Q("exists", field="price")
    
    # 13. IDs Query
    if 'ids' in request.GET:
        ids = request.GET.get('ids').split(',')
        query &= Q("ids", values=ids)
    
    # 14. Geo Distance Query
    if 'geo' in request.GET:
        query &= Q("geo_distance", distance="50km", location={"lat": 40.73, "lon": -73.93})
    
    # 15. Geo Bounding Box Query
    if 'geo_bounding_box' in request.GET:
        query &= Q("geo_bounding_box", location={
            "top_left": {"lat": 40, "lon": -74},
            "bottom_right": {"lat": 39, "lon": -70}
        })
    
    # 16. Edge Ngram Query
    if 'edge_ngram' in request.GET:
        query &= Q("edge_ngram", title="el")
    
    # 17. Highlighting Query
    highlight = {
        "fields": {
            "title": {},
            "description": {}
        }
    }
    
    # 18. Aggregations (Example for categories)
    aggregation = {
        "category_agg": {
            "terms": {
                "field": "category"
            }
        }
    }
    
    # 19. Span Queries
    if 'span' in request.GET:
        query &= Q("span_term", category="electronics")
    
    # 20. Script Score Query
    if 'script_score' in request.GET:
        query &= Q("function_score", query=Q("match_all"), script_score={
            "script": "doc['price'].value * factor"
        })
    
    # Execute the query
    result = ProductDocument.search().query(query).extra(from_=from_size, size=size).highlight(highlight).aggs(aggregation).execute()

    # Format results
    products = [
        {
            "title": hit.title,
            "description": hit.description,
            "category": hit.category,
            "price": hit.price,
            "brand": hit.brand,
            "sku": hit.sku,
            "thumbnail": hit.thumbnail,
            "score": hit.meta.score,
            "highlight": hit.meta.highlight if hasattr(hit.meta, 'highlight') else None
        }
        for hit in result
    ]
    
    # Aggregation result (category-wise count)
    aggregations = result.aggregations.category_agg.buckets if 'category_agg' in result.aggregations else []

    data["products"] = products
    data["aggregations"] = aggregations
    
    return JsonResponse(data)


def advanced_search_product(request):
    search_terms = request.GET.get('search', '')
    category = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    tags = request.GET.get('tags', '')
    sort_by = request.GET.get('sort_by', 'price')
    sort_order = request.GET.get('sort_order', 'asc')
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))

    query = Q("match_all")

    if search_terms:
        query &= Q("multi_match", query=search_terms, fields=["title", "description"])

    if category:
        query &= Q("term", category=category)

    if brand:
        query &= Q("term", brand=brand)

    if min_price and max_price:
        query &= Q("range", price={"gte": min_price, "lte": max_price})
    elif min_price:
        query &= Q("range", price={"gte": min_price})
    elif max_price:
        query &= Q("range", price={"lte": max_price})

    if tags:
        tags_list = tags.split(',')
        tag_queries = [Q("nested", path="tags", query=Q("terms", tags__tag=tags_list))]
        query &= Q("bool", should=tag_queries)

    result = ProductDocument.search().query(query)

    if sort_by and sort_order:
        result = result.sort({sort_by: {"order": sort_order}})

    result = result.extra(from_=(page - 1) * size, size=size)

    result = result.execute()

    products = [
        {
            "title": hit.title,
            "description": hit.description,
            "category": hit.category,
            "price": hit.price,
            "brand": hit.brand,
            "sku": hit.sku,
            "thumbnail": hit.thumbnail,
            "tags": [tag['tag'] for tag in hit.tags],
            "score": hit.meta.score,
        }
        for hit in result
    ]

    data = {
        "status": 200,
        "message": "Products fetched successfully",
        "products": products,
        "total": result.hits.total.value,
        "page": page,
        "size": size
    }

    return JsonResponse(data)
