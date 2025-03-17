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
## Now I will give instructions on running and setting up lambda trigger on uploading file as for powershell as I did
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
## Here I also advise checking the urls of the created resources so you can fix them in the lambda function. 

## I already have the zipped function in the repository so you can use that for deploying but also if something needed to be changed here how you can zip the function:
```sh
Compress-Archive -Path lambda_function.py -DestinationPath lambda_function.zip -Force
```

Deploy Lambda function:
```sh
awslocal lambda create-function `
    --function-name S3TriggeredLambda `
    --runtime python3.9 `
    --role arn:aws:iam::000000000000:role/lambda-role `
    --handler lambda_function.lambda_handler `
    --zip-file fileb://lambda_function.zip
```

Here verify that function was deployed:
```sh
awslocal lambda list-functions
```


## Configuring s3 to trigger lambda
1. Give s3 permission to invoke lambda:
```sh
awslocal lambda add-permission `
    --function-name S3TriggeredLambda `
    --statement-id s3invoke `
    --action "lambda:InvokeFunction" `
    --principal s3.amazonaws.com `
    --source-arn arn:aws:s3:::network-data-bucket
```

2. Set up S3 event notifications:
```sh
 awslocal s3api put-bucket-notification-configuration `
>>     --bucket network-data-bucket `
>>     --notification-configuration s3-config.json
```

3. Now you can verify notification settings:
```sh
awslocal s3api get-bucket-notification-configuration --bucket network-data-bucket
```

## Now we can manually test everything. I left the debug prints because different errors can happen during invoking and to understadn on which step the error occured.

Upload Sample Data to S3:
```sh
awslocal s3 cp s3-sample-data/sample_network.txt s3://network-optimization-bucket/
```

Check Lambda logs to see if it was triggered:
```sh
awslocal logs describe-log-streams --log-group-name /aws/lambda/S3TriggeredLambda
```

To see what the function logged we can run:
```sh
awslocal logs get-log-events `
    --log-group-name /aws/lambda/S3TriggeredLambda `
    --log-stream-name "2025/03/17/[$LATEST]xxxxxxx"
```
Where we replace xxxxxx with the latest stream name.

And finally we can check is SQS received our message from lambda function:
```sh
awslocal sqs receive-message --queue-url http://host.docker.internal:4566/000000000000/output-queue
```


# Some issues I faced and you may face also
## Updating lambda function:
If you modify lambda_function.py, you need to update the deployment:

1. Zip the new function
```sh
Compress-Archive -Path lambda_function.py -DestinationPath lambda_function.zip -Force
```

2. Update the function code
```sh
awslocal lambda update-function-code `
    --function-name S3TriggeredLambda `
    --zip-file fileb://lambda_function.zip
```

## Docker Host & LocalStack URL Issues
When running the Lambda function inside LocalStack, you might see this error:
```json
{
  "statusCode": 500,
  "body": "Error accessing S3: Could not connect to the endpoint URL: \"http://localhost:4566/network-data-bucket/sample_network.txt\""
}

```
Or, the function executes successfully, but no message appears in the SQS queue.

It is because since LocalStack runs inside Docker, AWS services running in LocalStack must be accessed using host.docker.internal instead of localhost. 

Change all localhost:4566 URLs in your Lambda function to:
```python
s3_client = boto3.client('s3', endpoint_url="http://host.docker.internal:4566")
sqs_client = boto3.client('sqs', endpoint_url="http://host.docker.internal:4566")
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