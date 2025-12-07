#!/bin/bash

set -e
export AWS_PAGER=""

APP_NAME="jewelry-app"
ENV_NAME="jewelry-env"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text --no-verify-ssl)
ECR_URL="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$APP_NAME"
IMAGE_TAG="latest"
ZIP_FILE="app-deploy.zip"
S3_BUCKET="jewelry-shop-s3-bucket"
S3_KEY="$APP_NAME/$ZIP_FILE"
SOLUTION_STACK="64bit Amazon Linux 2023 v4.6.3 running Docker"

# Ensure zip exists
if ! command -v zip &>/dev/null; then
  ZIP_PATH="/c/Program Files (x86)/GnuWin32/bin"
  [[ -f "$ZIP_PATH/zip.exe" ]] && export PATH="$PATH:$ZIP_PATH" || {
    echo " 'zip' not found."; exit 1;
  }
fi

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION --no-verify-ssl | docker login --username AWS --password-stdin $ECR_URL

echo "📦 Ensuring ECR repo exists..."
aws ecr describe-repositories --repository-names "$APP_NAME" --region "$REGION" --no-verify-ssl >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name "$APP_NAME" --region "$REGION" --no-verify-ssl

echo "🐳 Building Docker image..."
docker build -t $APP_NAME -f Dockerfile .

echo "🏷️ Tagging & pushing image..."
docker tag $APP_NAME:latest $ECR_URL:$IMAGE_TAG
docker push $ECR_URL:$IMAGE_TAG

echo "📝 Creating Dockerrun.aws.json..."
cat > Dockerrun.aws.json <<EOF
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "$ECR_URL:$IMAGE_TAG",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "80"
    }
  ]
}
EOF

echo "🗜️ Creating ZIP..."
rm -f $ZIP_FILE && zip $ZIP_FILE Dockerrun.aws.json > /dev/null

echo "☁️ Uploading ZIP to S3..."
aws s3 cp $ZIP_FILE s3://$S3_BUCKET/$S3_KEY --region $REGION --no-verify-ssl

echo "🧬 Ensuring Elastic Beanstalk application..."
aws elasticbeanstalk describe-applications --application-names "$APP_NAME" --region "$REGION" --no-verify-ssl \
  | grep "$APP_NAME" >/dev/null || \
  aws elasticbeanstalk create-application --application-name "$APP_NAME" --region "$REGION" --no-verify-ssl
VERSION_LABEL="v-$(date +%Y%m%d%H%M%S)"
echo "📌 Creating version $VERSION_LABEL..."
aws elasticbeanstalk create-application-version \
  --application-name "$APP_NAME" \
  --version-label "$VERSION_LABEL" \
  --source-bundle S3Bucket=$S3_BUCKET,S3Key=$S3_KEY \
  --region "$REGION" \
  --no-verify-ssl

echo "🧐 Checking environment status..."
ENV_STATUS=$(aws elasticbeanstalk describe-environments \
  --application-name "$APP_NAME" \
  --environment-names "$ENV_NAME" \
  --region "$REGION" \
  --query "Environments[0].Status" \
  --output text --no-verify-ssl 2>/dev/null || echo "NotFound")

if [[ "$ENV_STATUS" == "Ready" || "$ENV_STATUS" == "Launching" ]]; then
  echo "🔄 Updating environment..."
  aws elasticbeanstalk update-environment \
    --environment-name "$ENV_NAME" \
    --version-label "$VERSION_LABEL" \
    --region "$REGION" \
    --no-verify-ssl \
    --option-settings '[{
      "Namespace": "aws:autoscaling:asg",
      "OptionName": "MinSize",
      "Value": "2"
    },{
      "Namespace": "aws:autoscaling:asg",
      "OptionName": "MaxSize",
      "Value": "4"
    }]'
else
  echo "🚀 Creating new environment..."
  aws elasticbeanstalk create-environment \
    --application-name "$APP_NAME" \
    --environment-name "$ENV_NAME" \
    --version-label "$VERSION_LABEL" \
    --solution-stack-name "$SOLUTION_STACK" \
    --region "$REGION" \
    --no-verify-ssl \
    --option-settings '[{
      "Namespace": "aws:autoscaling:launchconfiguration",
      "OptionName": "IamInstanceProfile",
      "Value": "LabInstanceProfile"
    },{
      "Namespace": "aws:elasticbeanstalk:environment",
      "OptionName": "EnvironmentType",
      "Value": "LoadBalanced"
    },{
      "Namespace": "aws:elb:loadbalancer",
      "OptionName": "CrossZone",
      "Value": "true"
    },{
      "Namespace": "aws:elasticbeanstalk:application",
      "OptionName": "Application Healthcheck URL",
      "Value": "/"
    },{
      "Namespace": "aws:autoscaling:asg",
      "OptionName": "MinSize",
      "Value": "2"
    },{
      "Namespace": "aws:autoscaling:asg",
      "OptionName": "MaxSize",
      "Value": "4"
    }]'
fi

echo "✅ Deployment finished!"
aws elasticbeanstalk describe-environments \
  --application-name "$APP_NAME" \
  --region "$REGION" \
  --no-verify-ssl \
  --query "Environments[?EnvironmentName=='$ENV_NAME'].[CNAME,Status]" \
  --output table
