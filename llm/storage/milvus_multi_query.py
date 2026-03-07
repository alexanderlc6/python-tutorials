# Reference article: https://blog.csdn.net/qkh1234567/article/details/141160642
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, MilvusClient, utility
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
