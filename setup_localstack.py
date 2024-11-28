import boto3
import json

localstack_endpoint = 'http://localhost:4566'

# Initialize clients
apigateway_client = boto3.client('apigateway', endpoint_url=localstack_endpoint)
lambda_client = boto3.client('lambda', endpoint_url=localstack_endpoint)
s3_client = boto3.client('s3', endpoint_url=localstack_endpoint)
dynamodb_client = boto3.client('dynamodb', endpoint_url=localstack_endpoint)

# Create S3 bucket
s3_client.create_bucket(Bucket='my-bucket')

# Create DynamoDB table
dynamodb_client.create_table(
    TableName='Images',
    AttributeDefinitions=[
        {'AttributeName': 'imageId', 'AttributeType': 'S'}
    ],
    KeySchema=[
        {'AttributeName': 'imageId', 'KeyType': 'HASH'}
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Create Lambda function
def create_lambda_function(function_name, handler):
    with open('handler.py', 'rb') as f:
        zip_content = f.read()

    lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.7',
        Role='arn:aws:iam::000000000000:role/lambda-role',
        Handler=handler,
        Code={'ZipFile': zip_content},
        Timeout=30,
        MemorySize=128,
        Publish=True
    )

create_lambda_function('image_service', 'handler.lambda_handler')

# Create API Gateway
rest_api = apigateway_client.create_rest_api(name='image-service')
root_resource_id = apigateway_client.get_resources(restApiId=rest_api['id'])['items'][0]['id']

def create_resource_and_method(path, method):
    resource = apigateway_client.create_resource(
        restApiId=rest_api['id'],
        parentId=root_resource_id,
        pathPart=path
    )
    apigateway_client.put_method(
        restApiId=rest_api['id'],
        resourceId=resource['id'],
        httpMethod=method,
        authorizationType='NONE'
    )
    lambda_uri = f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:image_service/invocations'
    apigateway_client.put_integration(
        restApiId=rest_api['id'],
        resourceId=resource['id'],
        httpMethod=method,
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=lambda_uri
    )
    lambda_client.add_permission(
        FunctionName='image_service',
        StatementId=f'image_service-apigateway-{method}-{path}',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:us-east-1:000000000000:{rest_api["id"]}/*/{method}/{path}'
    )

create_resource_and_method('images/upload', 'POST')
create_resource_and_method('images', 'GET')
create_resource_and_method('images/{imageId}', 'GET')
create_resource_and_method('images/{imageId}', 'DELETE')

# Deploy API
apigateway_client.create_deployment(
    restApiId=rest_api['id'],
    stageName='dev'
)