import numpy as np
import requests
import json

# Generate 10000 mock vector records of 128 dimensions
np.random.seed(42)
vectors = np.random.randn(10000, 128)

# L2 normalization
vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

def index_batch(index_name, vectors, start_id = 0):
    '''Batch indexing data'''
    bulk_data = []
    for i, vec in enumerate(vectors):
        doc_id = start_id + i
        bulk_data.append(json.dumps({'index': {'_index': index_name, '_id': str(doc_id)}}))
        bulk_data.append(json.dumps({'id': doc_id, 'vector': vec.tolist()}))

    response = requests.post('http://localhost:9200/_bulk',
                             headers={'Content-Type': 'application/x-ndjson'},
                             data='\n'.join(bulk_data) + '\n'
                             )
    return response.json()

for idx_name in ['hnsw_test_low', 'hnsw_test_medium', 'hnsw_test_high']:
    index_batch(idx_name, vectors)
    print(f'Indexed to {idx_name}')

# Recall rate test
def brute_force_search(query_vec, all_vectors, k=100):
    '''
    Calculate all vector distances and return top k
    :param query_vec:
    :param all_vectors:
    :param k:
    :return:
    '''
    similarities = np.dot(all_vectors, query_vec)
    top_k_indices = np.argsort(similarities)[-k:][::-1]
    return set(top_k_indices)

def hnsw_search(index_name, query_vec, k=100, num_candidates=100):
    '''HNSW similarity search'''
    query = {
        'knn': {
            'field': 'vector',
            'query_vector': query_vec.tolist(),
            'k': k,
            'num_candidates': num_candidates
        },
        '_source': ['id']
    }

    response = requests.post(f'http://localhost:9200/{index_name}/_search', json=query).json()
    return {int(hit['_source']['id']) for hit in response['hits']['hits']}

def calculate_recall(groud_truth, approx_result):
    '''RecallRate = Intersection / g'''
    intersection = len(groud_truth & approx_result)
    return intersection / len(groud_truth)

test_queries = np.random.randn(100, 128)
test_queries = test_queries / np.linalg.norm(test_queries, axis=1, keepdims=True)
results = {
    'low': {'recalls':[], 'latencies': []},
    'medium': {'recalls': [],'latencies': []},
    'high': {'recalls': [],'latencies': []}
}

for query_vec in test_queries:
    # Get ground true(force search)
    gt = brute_force_search(query_vec, vectors, k=100)

    # Test different indexes
    for idx_name, key in [('hnsw_test_low', 'low'),('hnsw_test_medium', 'medium'),('hnsw_test_high', 'high')]:
        import time
        start = time.time()
        approx = hnsw_search(idx_name, query_vec, k=100, num_candidates=100)
        latency = (time.time() - start) * 1000

        recall = calculate_recall(gt, approx)
        results[key]['recalls'].append(recall)
        results[key]['latencies'].append(latency)

for key in results:
    avg_recall = np.mean(results[key]['recalls'])
    avg_latency = np.mean(results[key]['latencies'])
    print(f'{key}: Average recall rate:{avg_recall:.4f}, Average latency:{avg_latency}ms')

# ef(num_candidates) affect recall rate when query
# If ef up, recall rate will down(e.g. ef=10: ~70%, ef=50: ~88%, ef=100: ~93%, ef=200: ~96%, ef=500: ~98%)
num_candidates_list = [10, 50, 100, 200, 500]
recall_by_ef = {}

for ef in num_candidates_list:
    recalls = []
    for query_vec in test_queries[:20]:
        gt = brute_force_search(query_vec, vectors, k=10)
        approx = hnsw_search('hnsw_test_medium', query_vec, k=10, num_candidates=ef)
        recalls.append(calculate_recall(gt, approx))