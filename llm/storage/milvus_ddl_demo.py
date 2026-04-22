import json

from pymilvus import MilvusClient, DataType

client = MilvusClient("http://127.0.0.1:19530")

# Create schema
schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_filed = True)
client.drop_collection('test_coll')

# Add fields for schema
schema.add_field(field_name='id', datatype=DataType.INT64, is_primary=True)
schema.add_field(field_name='vector', datatype=DataType.FLOAT_VECTOR, dim=5)
schema.add_field(field_name='color', datatype=DataType.VARCHAR, max_length=64)
# schema.add_field(field_name='scalar_1', datatype=DataType.VARCHAR, max_length=64)
# schema.add_field(field_name='scalar_2', datatype=DataType.VARCHAR, max_length=64)
client.create_collection(collection_name='test_coll', dimension=5, schema=schema, metric_type='IP')

# Create index for collection
index_params = MilvusClient.prepare_index_params()
index_params.add_index(field_name='vector', metric_type = 'COSINE', index_name='vector_index')
client.create_index(collection_name='test_coll', index_params=index_params)

# Check indexes within the collection
res = client.list_indexes(collection_name='test_coll')
print(res)

# Check index details
res = client.describe_index(collection_name='test_coll', index_name='vector_index')
print(res)

# Delete index
# client.drop_index(collection_name='test_coll', index_name='vector_index')

# Create scalar index
# index_params2 = client.prepare_index_params(collection_name='test_coll')
# index_params2.add_index(field_name='scalar_1', index_type='INVERTED', index_name='inverted_index')
# client.create_index(collection_name='test_coll', index_params=index_params2)

# Create inverted index
# index_params3 = client.prepare_index_params()
# index_params3.add_index(field_name='scalar_2', index_type='INVERTED', index_name='inverted_index')
# client.create_index(collection_name='test_coll', index_params=index_params3)

# res = client.list_indexes(collection_name='test_coll')
# print(res)

