import json
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import NoCredentialsError
from handler import lambda_handler, upload_image, list_images, view_image, delete_image

@pytest.fixture
def mock_s3_client():
    with patch('handler.s3_client') as mock:
        yield mock

@pytest.fixture
def mock_dynamodb_client():
    with patch('handler.dynamodb_client') as mock:
        yield mock

def test_lambda_handler_upload_image(mock_s3_client, mock_dynamodb_client):
    event = {
        'httpMethod': 'POST',
        'path': '/images/upload',
        'body': json.dumps({
            'image': 'test_image_data',
            'metadata': {'key': 'value'}
        })
    }
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    assert 'imageId' in json.loads(response['body'])
    mock_s3_client.put_object.assert_called_once()
    mock_dynamodb_client.put_item.assert_called_once()

def test_lambda_handler_list_images(mock_dynamodb_client):
    event = {
        'httpMethod': 'GET',
        'path': '/images',
        'queryStringParameters': {}
    }
    mock_dynamodb_client.scan.return_value = {'Items': []}
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == []

def test_lambda_handler_view_image(mock_s3_client):
    event = {
        'httpMethod': 'GET',
        'path': '/images/test-image-id',
        'pathParameters': {'imageId': 'test-image-id'}
    }
    mock_s3_client.generate_presigned_url.return_value = 'http://example.com/test-image-id.jpg'
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    assert 'url' in json.loads(response['body'])

def test_lambda_handler_delete_image(mock_s3_client, mock_dynamodb_client):
    event = {
        'httpMethod': 'DELETE',
        'path': '/images/test-image-id',
        'pathParameters': {'imageId': 'test-image-id'}
    }
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['message'] == 'Image deleted successfully'
    mock_s3_client.delete_object.assert_called_once()
    mock_dynamodb_client.delete_item.assert_called_once()

def test_upload_image_no_credentials(mock_s3_client):
    mock_s3_client.put_object.side_effect = NoCredentialsError
    event = {
        'body': json.dumps({
            'image': 'test_image_data',
            'metadata': {'key': 'value'}
        })
    }
    response = upload_image(event)
    assert response['statusCode'] == 500
    assert json.loads(response['body'])['error'] == 'Credentials not available'

def test_list_images_no_credentials(mock_dynamodb_client):
    mock_dynamodb_client.scan.side_effect = NoCredentialsError
    event = {
        'queryStringParameters': {}
    }
    response = list_images(event)
    assert response['statusCode'] == 500
    assert json.loads(response['body'])['error'] == 'Credentials not available'

def test_view_image_no_credentials(mock_s3_client):
    mock_s3_client.generate_presigned_url.side_effect = NoCredentialsError
    event = {
        'pathParameters': {'imageId': 'test-image-id'}
    }
    response = view_image(event)
    assert response['statusCode'] == 500
    assert json.loads(response['body'])['error'] == 'Credentials not available'

def test_delete_image_no_credentials(mock_s3_client):
    mock_s3_client.delete_object.side_effect = NoCredentialsError
    event = {
        'pathParameters': {'imageId': 'test-image-id'}
    }
    response = delete_image(event)
    assert response['statusCode'] == 500
    assert json.loads(response['body'])['error'] == 'Credentials not available'