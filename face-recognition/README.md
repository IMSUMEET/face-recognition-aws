# Creating face-recognition lambda

## Steps:

1. Since there are lot of dependencies we will deploy this lambda using container image as ECR (elastic container registery)
2. Create a new ecr repository. Name it something like "face-recognition-lambda"
3. We will create a docker image and push it to our ecr repository.
