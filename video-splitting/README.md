# Creating video-splitting lambda

## Steps:

1. Create a new lambda function in aws lambda
2. Inside console editor of lambda copy and paste the video-splitting.py code
3. We avoid putting ffmpeg external dependency inside the lambda using ecr. This is help reduce unnecessary ecr usage.
4. Instead we will put the ffmpeg file using lambda layer over the lambda function.
5. Create a zip of the ffmpeg.

- Download the excutable for ffmpeg. [Download link](https://www.ffmpeg.org/download.html)
- Create a folder called ffmpeglib and copy the ffmpeg executable from the downloaded folder inside ffmpeglib
- Zip the ffmpeglib. (ffmpeglib.zip)

6. Create a new layer in aws called "ffmpeg-layer".
7. create layer using the zip we just created
8. Add this layer to the video-splitting lambda.
9. Add a trigger for s3 input bucket. So whenever there is an input inside input bucket it should trigger the video-splitting lambda.
10. Create a role inside IAM that has following policies:

- S3BucketAccessPolicy
- AWSLambdaBasicExecutionRole
- AllowInvokeFaceRecognition

11. Add this role as an execution role for the lambda.
12. With that we have succesfully created a video-splitting lambda that splits the .mp4 file uploaded to input bucket into 1 frame and stores inside stage-1 bucket.
13. Further we will invoke another lambda "face-recognition" that will then use the data.pt file to recognize faces and store the .txt file as output inside output bucket.
