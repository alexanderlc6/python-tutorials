# Reference article: https://blog.csdn.net/qkh1234567/article/details/141160642
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, MilvusClient, utility, AnnSearchRequest, WeightedRanker
import random

connections.connect(host="127.0.0.1", port="19530")
# client = MilvusClient("http://127.0.0.1:19530")
collection_name = "movie"

# Use MilvusClient instead
# if client.has_collection(collection_name):
#     client.drop_collection(collection_name)
#     print("Collection dropped")
#
# client.create_collection(collection_name, dimension=5, auto_id=False, primary_field_name='film_id',
#                          vector_field_name='filmVector', enable_dynamic_field=True)
# client.add_collection_field(collection_name, field_name='posterVector', data_type=DataType.FLOAT_VECTOR, dim=5,
#                             nullable={})

if utility.has_collection(collection_name):
    utility.drop_collection(collection_name)
    print("Collection dropped")

# Create schema demo
fields = [
    FieldSchema(name="film_id", dtype=DataType.INT64, is_primary=True),
    FieldSchema(name="filmVector", dtype=DataType.FLOAT_VECTOR, dim=5),
    FieldSchema(name="posterVector", dtype=DataType.FLOAT_VECTOR, dim=5)
]

schema = CollectionSchema(fields=fields, description="movie collection", enable_dynamic_field = True)
coll = Collection(name="movie", schema=schema)

index_params = {
    'metric_type': 'L2',
    'index_type': 'IVF_FLAT',
    'params': {"nlist": 1024}
}
coll.create_index(field_name='filmVector', index_params=index_params)
coll.create_index(field_name='posterVector', index_params=index_params)
print("Index created")

entities = []

for _ in range(1000):
    film_id = random.randint(1, 1000)
    film_vector = [random.random() for _ in range(5)]
    poster_vector = [random.random() for _ in range(5)]

    entity = {
        "film_id": film_id,
        "filmVector": film_vector,
        "posterVector": poster_vector
    }
    entities.append(entity)

coll.insert(entities)
print(f"Data inserted { len(entities)} records.")
coll.load()


# ===== ANN Search demo ======
# Create multi search request for field [filmVector]
query_filmVector = [[0.8896863042430693, 0.370613100114602, 0.23779315077113428, 0.38227915951132996, 0.5997064603128835]]

search_params_1 = {
    'data': query_filmVector,
    'anns_field': 'filmVector',
    'param': {
        'metric_type': 'L2',
        'params': {
            'nprobe': 10
        }
    },
    'limit': 2
}

request_1 = AnnSearchRequest(**search_params_1)

query_posterVector = [[0.02550758562349764, 0.006085637357292062, 0.5325251250159071, 0.7676432650114147, 0.5521074424751443]]

search_params_2 = {
    'data': query_posterVector,
    'anns_field': 'posterVector',
    'param': {
        'metric_type': 'L2',
        'params': {
            'nprobe': 10
        }
    },
    'limit': 2
}
request_2 = AnnSearchRequest(**search_params_2)
reqs = [request_1, request_2]

# Config rank strategy
# Given text search weight 0.8 and image search weight 0.2
rerank = WeightedRanker(0.8, 0.2)

coll.load()
res = coll.hybrid_search(reqs, rerank, limit = 2)
print(res)