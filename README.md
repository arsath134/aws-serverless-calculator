# AWS Serverless Calculator

A simple mathematical calculator built using AWS EC2, API Gateway, Lambda, and DynamoDB.

## How It Works

EC2 → API Gateway → Lambda → DynamoDB

1. User enters a mathematical expression on the EC2 webpage.
2. API Gateway sends the request to Lambda.
3. Lambda performs the calculation.
4. Lambda stores the result in DynamoDB.
5. The result is displayed on the webpage.

## AWS Services

* EC2 - Hosts the calculator frontend
* API Gateway - Provides the API endpoint
* Lambda - Performs the calculation
* DynamoDB - Stores calculation results
* IAM - Provides Lambda permissions

## IAM Role

Role: `AWS-Calculator-Lambda-Role`

Policies:

* `AWSLambdaBasicExecutionRole`
* `AmazonDynamoDBFullAccess`

## DynamoDB

Table: `calculations`

Partition Key: `calculations_id`

Type: `String`

## Run the Project

1. Deploy `lambda_function.py` to Lambda.
2. Create the DynamoDB table.
3. Create API Gateway with `POST /calculator`.
4. Add the API Gateway URL to `frontend/app.js`.
5. Copy the frontend files to EC2.
6. Run:

```bash
python3 -m http.server 8080 --bind 0.0.0.0
```

7. Open:

`http://EC2_PUBLIC_IP:8080`

## Example

Enter:

`25 + 15`

Lambda calculates:

`40`

The result is displayed on the EC2 webpage and stored in DynamoDB.
