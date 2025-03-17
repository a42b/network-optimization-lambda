import json
import boto3
import os

# LocalStack AWS credentials (used for local testing)
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Connect to LocalStack
s3_client = boto3.client('s3', endpoint_url="http://host.docker.internal:4566")
sqs_client = boto3.client('sqs', endpoint_url="http://host.docker.internal:4566")

SQS_QUEUE_URL = "http://host.docker.internal:4566/000000000000/output-queue"
def compute_mst(num_nodes, edges):
    """ Implements Kruskal's Algorithm to compute the Minimum Spanning Tree """
    print("⏳ Starting MST computation...")
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

    print(f"MST Computed! Total Cost: {total_cost}, Edges: {mst_edges}")
    return total_cost, mst_edges

def lambda_handler(event, context):
    print("Lambda triggered with event:", json.dumps(event, indent=2))
    
    try:
        record = event["Records"][0]
        bucket_name = record["s3"]["bucket"]["name"]
        file_key = record["s3"]["object"]["key"]

        print(f"Fetching file from S3: s3://{bucket_name}/{file_key}")

        # Get S3 file
        try:
            print(f"Attempting to get S3 file: Bucket={bucket_name}, Key={file_key}")
            file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            file_content = file_obj["Body"].read().decode("utf-8")
            print("File successfully retrieved from S3!")
        except Exception as s3_error:
            print(f"Error accessing S3: {str(s3_error)}")
            return {"statusCode": 500, "body": f"Error accessing S3: {str(s3_error)}"}

        print("File successfully retrieved from S3!")

        # Parse file content
        lines = file_content.strip().split("\n")
        num_nodes = int(lines[0])
        edges = []
        for line in lines[1:]:
            node1, node2, cost = map(int, line.split())
            edges.append((cost, node1, node2))

        # Compute Minimum Spanning Tree
        total_cost, mst_edges = compute_mst(num_nodes, edges)

        message = {
            "total_cost": total_cost,
            "connections": [{"from": u, "to": v, "cost": c} for c, u, v in mst_edges],
            "s3_file_path": f"s3://{bucket_name}/{file_key}"
        }

        print("Sending message to SQS:", json.dumps(message, indent=2))

        # Send result to SQS
        try:
            response = sqs_client.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(message)
            )
            print(f"SQS Message Sent! Message ID: {response['MessageId']}")
        except Exception as sqs_error:
            print(f"Error sending message to SQS: {str(sqs_error)}")
            return {"statusCode": 500, "body": f"Error sending message to SQS: {str(sqs_error)}"}

        return {"statusCode": 200, "body": "Processing complete, result sent to SQS."}

    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}

