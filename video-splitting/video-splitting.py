import os
import boto3
import json
import time
import subprocess

# Initialize S3 client and Lambda client
s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    # Log the incoming event for debugging purposes
    print("Received event: ", event)
    
    # Get bucket name and object key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Define the path to download the video file
    download_path = f'/tmp/{os.path.basename(key)}'
    
    # Download the video file from S3
    try:
        s3.download_file(bucket, key, download_path)
        print(f"Downloaded {key} from bucket {bucket} to {download_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")
        return {
            'statusCode': 500,
            'body': f"Error downloading file: {e}"
        }

    # Start timing the video processing
    start_time = time.time()

    # Log the environment path and check if ffmpeg is executable
    ffmpeg_path = '/opt/ffmpeglib/ffmpeg'
    if os.path.exists(ffmpeg_path):
        file_stat = os.stat(ffmpeg_path)
        print(f"FFmpeg path: {ffmpeg_path}")
        print(f"FFmpeg permissions: {oct(file_stat.st_mode)}")
    else:
        print(f"FFmpeg not found at {ffmpeg_path}")

    # Check the ffmpeg version to confirm it's executable
    try:
        ffmpeg_version = subprocess.check_output([ffmpeg_path, '-version'])
        print(f"FFmpeg version: {ffmpeg_version.decode('utf-8')}")
    except Exception as e:
        print(f"Error executing ffmpeg: {e}")
        return {
            'statusCode': 500,
            'body': f"Error executing ffmpeg: {e}"
        }

    # Call the video-splitting function
    try:
        # Get the folder name based on the input video name
        video_name_without_extension = os.path.splitext(os.path.basename(key))[0]
        generated_images = video_splitting_cmdline(download_path, video_name_without_extension)
        if not generated_images:
            print("No frames generated from the video.")
            return {
                'statusCode': 500,
                'body': "No frames generated from the video."
            }
        print(f"Frames generated: {len(generated_images)}")
    except Exception as e:
        print(f"Error generating frames: {e}")
        return {
            'statusCode': 500,
            'body': f"Error generating frames: {e}"
        }

    # Define the S3 path to upload the image (without folder structure)
    upload_bucket = f'{bucket.replace("-input", "-stage-1")}'
    
    # Upload the single generated image to S3
    if generated_images:
        image_path = generated_images[0]  # Only use the first generated image (one frame)
        output_image_name = f'{video_name_without_extension}.jpg'  # Use video name for the image file
        upload_key = output_image_name  # Just use the image file name, not inside a folder

        # Upload the generated image to S3
        try:
            s3.upload_file(image_path, upload_bucket, upload_key)
            print(f"Uploaded {output_image_name} to {upload_bucket}/{upload_key}")
        except Exception as e:
            print(f"Error uploading {output_image_name}: {e}")
        
        # Invoke the face-recognition Lambda function asynchronously
        try:
            response = lambda_client.invoke(
                FunctionName='face-recognition',
                InvocationType='Event',  # Asynchronous invocation
                Payload=json.dumps({
                    'bucket_name': upload_bucket,
                    'image_file_name': upload_key
                })
            )

            # Log the response from face-recognition Lambda
            print(f"Response from face-recognition: {response['Payload'].read().decode('utf-8')}")
        except Exception as e:
            print(f"Error invoking face-recognition: {e}")

    # End timing and check execution duration
    duration = time.time() - start_time
    print(f"Processing time for {key}: {duration:.2f} seconds")

    return {
        'statusCode': 200,
        'body': f"Successfully processed {key} and uploaded image to {upload_bucket}"
    }


def video_splitting_cmdline(video_filename, video_name_without_extension):
    # Create output directory based on the input video filename
    output_dir = f'/tmp/{video_name_without_extension}'
    os.makedirs(output_dir, exist_ok=True)

    # ffmpeg command to split video into exactly 1 frame
    split_cmd = [
        '/opt/ffmpeglib/ffmpeg',
        '-i', video_filename,
        '-vf', 'fps=1',              # Capture 1 frame per second (you can change fps to extract another frame if needed)
        '-frames:v', '1',             # Limit to 1 frame (only the first frame will be extracted)
        f'{output_dir}/{video_name_without_extension}.jpg', # Output file with same name as video
        '-y'                          # Overwrite output files without asking
    ]

    try:
        # Run the ffmpeg command
        subprocess.check_call(split_cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.returncode}")

    # Dynamically get the list of generated images, assuming only one image is generated
    generated_images = [os.path.join(output_dir, f) for f in sorted(os.listdir(output_dir)) if f.endswith('.jpg')]

    return generated_images
