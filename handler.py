import json
import boto3
import logging
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

s3_client = boto3.client('s3', endpoint_url='http://localhost:4566')
# dynamodb_client = boto3.client('dynamodb', endpoint_url='http://localhost:4566')

def lambda_handler(event, context):
    """
    Entry point for the Lambda function. Routes the request to the appropriate handler function
    based on the HTTP method and path.

    Parameters:
    event (dict): The event dictionary containing request data.
    context (object): The context object containing runtime information.

    Returns:
    dict: The response dictionary containing statusCode and body.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    http_method = event['httpMethod']
    path = event['path']
    
    if http_method == 'POST' and path == '/images/upload':
        return upload_image(event)
    elif http_method == 'GET' and path == '/images':
        return list_images(event)
    elif http_method == 'GET' and path.startswith('/images/'):
        return view_image(event)
    elif http_method == 'DELETE' and path.startswith('/images/'):
        return delete_image(event)
    else:
        logger.warning(f"Received unsupported path: {path}")
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not Found'})
        }

def upload_image(event):
    """
    Handles the upload of an image. Stores the image in S3 and metadata in DynamoDB.

    Parameters:
    event (dict): The event dictionary containing request data.

    Returns:
    dict: The response dictionary containing statusCode and body.
    """
    try:
        body = json.loads(event['body'])
        image = body['image']
        metadata = body['metadata']
        image_id = str(uuid4())
        
        logger.info(f"Uploading image with ID: {image_id}")
        
        s3_client.put_object(Bucket='my-bucket', Key=f'{image_id}.jpg', Body=image)
        
        dynamodb_client.put_item(
            TableName='Images',
            Item={
                'imageId': {'S': image_id},
                'metadata': {'S': json.dumps(metadata)}
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'imageId': image_id})
        }
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Something went wrong'})
        }

def list_images(event):
    """
    Lists all images stored in DynamoDB. Can filter images based on metadata.

    Parameters:
    event (dict): The event dictionary containing request data.

    Returns:
    dict: The response dictionary containing statusCode and body.
    """
    try:
        filter1 = event['queryStringParameters'].get('filter1')
        filter2 = event['queryStringParameters'].get('filter2')
        
        logger.info("Listing images with filters: filter1=%s, filter2=%s", filter1, filter2)
        
        response = dynamodb_client.scan(TableName='Images')
        items = response['Items']
        
        if filter1:
            items = [item for item in items if filter1 in item['metadata']['S']]
        if filter2:
            items = [item for item in items if filter2 in item['metadata']['S']]
        
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }

    except Exception as e:
        logger.error(f"Error listing images: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Something went wrong'})
        }

def view_image(event):
    """
    Generates a presigned URL for viewing an image stored in S3.

    Parameters:
    event (dict): The event dictionary containing request data.

    Returns:
    dict: The response dictionary containing statusCode and body.
    """
    try:
        image_id = event['pathParameters']['imageId']
        
        logger.info(f"Generating presigned URL for image ID: {image_id}")
        
        url = s3_client.generate_presigned_url('get_object', Params={'Bucket': 'my-bucket', 'Key': f'{image_id}.jpg'}, ExpiresIn=3600)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'url': url})
        }

    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Something went wrong'})
        }

def delete_image(event):
    """
    Deletes an image from S3 and its metadata from DynamoDB.

    Parameters:
    event (dict): The event dictionary containing request data.

    Returns:
    dict: The response dictionary containing statusCode and body.
    """
    try:
        image_id = event['pathParameters']['imageId']
        
        logger.info(f"Deleting image with ID: {image_id}")
        
        s3_client.delete_object(Bucket='my-bucket', Key=f'{image_id}.jpg')
        
        dynamodb_client.delete_item(TableName='Images', Key={'imageId': {'S': image_id}})
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image deleted successfully'})
        }

    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Something went wrong'})
        }