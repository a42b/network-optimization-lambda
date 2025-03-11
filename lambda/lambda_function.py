import json
import boto3
import os

# LocalStack AWS credentials (fake, used for local testing)
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Connect to LocalStack
s3_client = boto3.client('s3', endpoint_url="http://localhost:4566")
sqs_client = boto3.client('sqs', endpoint_url="http://localhost:4566")

print("🔗 Environment variables set!")  

SQS_QUEUE_URL = "http://localhost:4566/000000000000/output-queue"

def compute_mst(num_nodes, edges):
    """ Implements Kruskal's Algorithm to compute the Minimum Spanning Tree """
    edges.sort()  # Sort edges by cost
    parent = {i: i for i in range(1, num_nodes + 1)}

    def find(node):
        if parent[node] != node:
            parent[node] = find(parent[node])
        return parent[node]

    def union(node1, node2):
        root1, root2 = find(node1), find(node2)
        if root1 != root2:
            parent[root2] = root1

    total_cost = 0
    mst_edges = []

    for cost, node1, node2 in edges:
        if find(node1) != find(node2):  # Avoid cycles
            union(node1, node2)
            mst_edges.append((cost, node1, node2))
            total_cost += cost

    return total_cost, mst_edges


def lambda_handler(event=None, context=None):  # Allow manual execution

    bucket_name = "network-optimization-bucket"
    file_key = "sample_network.txt"

    file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    file_content = file_obj['Body'].read().decode('utf-8')
    lines = file_content.strip().split("\n")

    num_nodes = int(lines[0])
    edges = []
    for line in lines[1:]:
        node1, node2, cost = map(int, line.split())
        edges.append((cost, node1, node2))

    total_cost, mst_edges = compute_mst(num_nodes, edges)

    message = {
        "total_cost": total_cost,
        "connections": [{"from": u, "to": v, "cost": c} for c, u, v in mst_edges],
        "s3_file_path": f"s3://{bucket_name}/{file_key}"
    }
    
    response = sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(message)
    )

    return {"statusCode": 200, "body": "Processing complete, result sent to SQS."}

lambda_handler()
