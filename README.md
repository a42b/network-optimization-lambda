# AWS Lambda Network Optimization 

## Overview
This project implements an **AWS Lambda function** that:
- **Watches an S3 bucket** for new network connection files.
- **Processes the network graph** to compute the **Minimum Spanning Tree (MST)**.
- **Sends the results to an SQS queue**.

###  Technologies Used
- **AWS Lambda** (Simulated with LocalStack)
- **AWS S3** 
- **AWS SQS** 
- **Python 3.x** 
- **LocalStack** 

---


## **Setup Instructions**
This project is built to **run locally** without an AWS account using **LocalStack**.

### **Install Dependencies**
Ensure you have **Python 3.8+**, then install required packages:
```sh
pip install localstack awscli-local boto3
```

Run LocalStack to simulate AWS services:
```sh
localstack start -d
```

Check if LocalStack is running:
```sh
localstack status
```

Create an S3 bucket:
```sh
awslocal s3 mb s3://network-optimization-bucket
```

Create an SQS queue:
```sh
awslocal s3 mb s3://network-optimization-bucket
```

Verify created resources:
```sh
awslocal s3 ls
awslocal sqs list-queues
```

Upload Sample Data to S3:
```sh
awslocal s3 cp s3-sample-data/sample_network.txt s3://network-optimization-bucket/
```

Now, execute the AWS Lambda function locally:
```sh
python lambda/lambda_function.py
```

## Testing
Check if a message was sent

```sh
awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/output-queue
```

Run Unit Tests
```sh
python -m unittest lambda/test_lambda.py
```