# API Documentation and Usage Instructions

## Lambda Function: `lambda_handler`

### Description
Entry point for the Lambda function. Routes the request to the appropriate handler function based on the HTTP method and path.

### Parameters
- `event` (dict): The event dictionary containing request data.
- `context` (object): The context object containing runtime information.

### Returns
- `dict`: The response dictionary containing `statusCode` and `body`.

## Function: `upload_image`

### Description
Handles the upload of an image. Stores the image in S3 and metadata in DynamoDB.

### Parameters
- `event` (dict): The event dictionary containing request data.

### Returns
- `dict`: The response dictionary containing `statusCode` and `body`.

## Function: `list_images`

### Description
Lists all images stored in DynamoDB. Can filter images based on metadata.

### Parameters
- `event` (dict): The event dictionary containing request data.

### Returns
- `dict`: The response dictionary containing `statusCode` and `body`.

## Function: `view_image`

### Description
Generates a presigned URL for viewing an image stored in S3.

### Parameters
- `event` (dict): The event dictionary containing request data.

### Returns
- `dict`: The response dictionary containing `statusCode` and `body`.

## Function: `delete_image`

### Description
Deletes an image from S3 and its metadata from DynamoDB.

### Parameters
- `event` (dict): The event dictionary containing request data.

### Returns
- `dict`: The response dictionary containing `statusCode` and `body`.

## Usage Instructions

### Upload Image

#### Request
- **Method**: POST
- **Path**: `/images/upload`
- **Body**:
  ```json
  {
    "image": "base64_encoded_image_data",
    "metadata": {
      "key": "value"
    }
  }
  #### Response
- **Status Code**: 200
- **Body**:
  ```json
  {
    "imageId": "generated_image_id"
  }
  ```

### 2. List Images

#### Request
- **Method**: GET
- **Path**: `/images`
- **Query Parameters** (optional):
  - `filter1`: Filter based on metadata.
  - `filter2`: Filter based on metadata.

#### Response
- **Status Code**: 200
- **Body**:
  ```json
  [
    {
      "imageId": "image_id",
      "metadata": "metadata_json_string"
    },
    ...
  ]
  ```

### 3. View Image

#### Request
- **Method**: GET
- **Path**: `/images/{imageId}`
- **Path Parameters**:
  - `imageId`: The ID of the image to view.

#### Response
- **Status Code**: 200
- **Body**:
  ```json
  {
    "url": "presigned_url_to_view_image"
  }
  ```

### 4. Delete Image

#### Request
- **Method**: DELETE
- **Path**: `/images/{imageId}`
- **Path Parameters**:
  - `imageId`: The ID of the image to delete.

#### Response
- **Status Code**: 200
- **Body**:
  ```json
  {
    "message": "Image deleted successfully"
  }#   i n s t a g r a m _ i m a g e s  
 