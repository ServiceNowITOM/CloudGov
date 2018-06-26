import boto3
from datetime import datetime, timedelta

#Get current time for tag value
def GetCurrentTimeTag():
    now = (datetime.now() - timedelta(hours=4))

    if now.hour  > 12:
        return str(now.hour - 12) + "PM"
        
    if now.hour < 12:
        return str(now.hour) + "AM"
        
    if now.hour == 12:
        return "12PM"


# Find Instances that should be powered Off
def OffInstances(tagtime):
    client = boto3.client('ec2')
    response = client.describe_tags(
        DryRun=False,
        Filters = [{'Name':'tag:StopAt', 'Values':[tagtime]}],
    MaxResults=10000
)
    resIDs = []
    for x in response['Tags']:
        resIDs.append(x['ResourceId'])
    return resIDs

# Find Instances that should be powered On
def OnInstances(tagtime):
    client = boto3.client('ec2')
    response = client.describe_tags(
        DryRun=False,
        Filters = [{'Name':'tag:StartAt', 'Values':[tagtime]}],
    MaxResults=10000
)
    resIDs = []
    for x in response['Tags']:
        resIDs.append(x['ResourceId'])
    return resIDs

def PowerOnEC2(resIDs):
    ec2 = boto3.client('ec2')
    ec2.start_instances(InstanceIds=resIDs)

def PowerOffEC2(resIDs):
    ec2 = boto3.client('ec2')
    ec2.stop_instances(InstanceIds=resIDs)
    

#def lambda_handler(event, context):
##    ec2 = boto3.client('ec2', region_name=region)
 #   ec2.start_instances(InstanceIds=instances)
 #   print 'started your instances: ' + str(instances)



def lambda_handler(event, context):
    tagtime = GetCurrentTimeTag()
    OffresIDs = OffInstances(tagtime)
    if len(OffresIDs) > 0:
        PowerOffEC2(OffresIDs)
    OnresIDs = OnInstances(tagtime)
    if len(OnresIDs) > 0:
        PowerOnEC2(OnresIDs)
    
