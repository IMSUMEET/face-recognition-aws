import os
import cv2
import json
import boto3
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import warnings
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

warnings.filterwarnings('ignore')
torch.set_grad_enabled(False)

s3_client = boto3.client('s3', region_name='us-east-1')

os.environ['TORCH_HOME'] = '/tmp'
device = torch.device('cpu')
torch.set_num_threads(1)

mtcnn = MTCNN(
    image_size=240,
    margin=0,
    min_face_size=20,
    thresholds=[0.5, 0.6, 0.6],
    device=device,
    post_process=True
)
resnet = InceptionResnetV1(pretrained='vggface2', device=device).eval()

def handler(event, context):
    try:
        logger.info("Handler triggered with event: %s", event)

        os.makedirs('/tmp/models', exist_ok=True)
        os.makedirs('/tmp/checkpoints', exist_ok=True)

        # Extract input bucket and dynamically determine other buckets
        bucket_name = event['bucket_name']
        image_file_name = event['image_file_name']
        logger.info("Input bucket: %s, Image file name: %s", bucket_name, image_file_name)

        asu_id = bucket_name.replace("-stage-1", "")  # Extract ASU ID from bucket name
        data_bucket = f"{asu_id}-data"
        output_bucket = f"{asu_id}-output"
        logger.info("Extracted ASU ID: %s, Data bucket: %s, Output bucket: %s", asu_id, data_bucket, output_bucket)

        input_path = f"/tmp/{image_file_name}"

        # Download image and model data from S3
        logger.info("Downloading image from bucket: %s, key: %s", bucket_name, image_file_name)
        s3_client.download_file(bucket_name, image_file_name, input_path)

        logger.info("Downloading data.pt from bucket: %s", data_bucket)
        s3_client.download_file(data_bucket, "data.pt", "/tmp/data.pt")

        # Process image
        logger.info("Reading the downloaded image: %s", input_path)
        img = cv2.imread(input_path, cv2.IMREAD_COLOR)
        if img is None:
            raise Exception(f"Failed to read image: {image_file_name}")

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        logger.info("Running face detection on the image")
        face, prob = mtcnn(img_pil, return_prob=True)
        if face is None:
            raise Exception("No face detected")

        # Recognize face
        logger.info("Loading embeddings from data.pt")
        saved_data = torch.load('/tmp/data.pt', map_location='cpu')

        logger.info("Computing face embeddings and comparing with database")
        emb = resnet(face.unsqueeze(0)).detach()
        dist_list = [torch.dist(emb, emb_db).item() for emb_db in saved_data[0]]
        idx_min = dist_list.index(min(dist_list))
        result = saved_data[1][idx_min]
        logger.info("Recognition result: %s", result)

        # Save result to file and upload to S3
        output_file = os.path.splitext(image_file_name)[0] + '.txt'
        output_path = f"/tmp/{output_file}"
        logger.info("Saving result to file: %s", output_path)
        with open(output_path, 'w') as f:
            f.write(result)

        logger.info("Uploading result file to bucket: %s, key: %s", output_bucket, output_file)
        s3_client.upload_file(output_path, output_bucket, output_file)

        logger.info("Upload successful")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Face recognition completed',
                'result': result,
                'output_file': output_file
            })
        }

    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        try:
            logger.info("Cleaning up /tmp directory")
            for filename in os.listdir('/tmp'):
                file_path = os.path.join('/tmp', filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error("Error during cleanup: %s", str(e))

