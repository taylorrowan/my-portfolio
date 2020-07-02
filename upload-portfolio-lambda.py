import json
import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:633697120677:deployPortfolioTopic')
    
    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        
        portfolio_bucket = s3.Bucket('portfolio.taylorrowan.io')
        build_bucket = s3.Bucket('portfoliobuild.taylorrowan.io')
        
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
        	for nm in myzip.namelist():
        		obj = myzip.open(nm)
        		portfolio_bucket.upload_fileobj(obj, nm,
    			ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
        		portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
    
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed successfully!")
    except:
        topic.publish(Subject="Portfolio Deploy Fail", Message="Portfolio Not Deployed Successfully!")
        raise
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
