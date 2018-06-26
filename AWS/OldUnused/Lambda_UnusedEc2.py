import boto3
from datetime import datetime, timedelta


# Find Instances older than days that are powered on
def OldInstances(instances, days):
    resIDs = []
    for instance in instances:
        now = datetime.now().astimezone()
            #nownew = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, tzinfo="utc")
        timeToCheck = (now - timedelta(hours=(days * 24)))
        if instance.launch_time < timeToCheck:
            resIDs.append(instance.instance_id)
        #if instance['LaunchTime'] < timeToCheck:
        #        resIDs.append(instance['InstanceId'])
    return resIDs

    


def IsCPUOver(perc, instance, days):
    cw = boto3.client('cloudwatch')
    now = datetime.now().astimezone()
    stats = cw.get_metric_statistics(
        Period=3600,
        StartTime=datetime.now().astimezone() - timedelta(hours=(days * 24)),
        EndTime=datetime.now().astimezone(),
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistics=['Maximum'],
        Dimensions=[{'Name':'InstanceId', 'Value':instance}]
        )
    
    for dp in stats['Datapoints']:
        if (dp['Maximum'] > perc):
            return True
        

def getAllInstances():
    instances = [i for i in boto3.resource('ec2').instances.all()]
    return instances
    


def findMissingTags(instances, neededtags):
    missingInstances = []
    if len(neededtags) > 0:
        for i in instances:
            for mytag in neededtags:
                if i.tags !=None:
                    if str(mytag) not in [t['Key'] for t in i.tags]:
                        missingInstances.append(i)
        return list(set(missingInstances))
    else:
        return instances
        
        

def PowerOffEC2(resIDs):
    ec2 = boto3.client('ec2')
    ec2.stop_instances(InstanceIds=resIDs)

def tagAndPowerOff(instance):
    ec2 = boto3.client('ec2')
    resIDs = []
    resIDs.append(instance.instance_id)
    ec2.create_tags(Resources=resIDs, Tags=[{'Key':'FlaggedUnused', 'Value':'True'}])
    #PowerOffEC2(resIDs)

def lambda_handler(event, context):
    #days to go back
    days = 30
    
    #Tags to ID systems to execute on
    mytags = []
    #Leave as an empty array unless need to define select systems
    #Example
    #mytags.append('KeyOfTag')
    
    #Exclude Machines that were identified already
    #This is a safety net so we dont keep powering machines off that are being used. 
    mytags.append('FlaggedUnused')
    
    #Get all instances
    instances = getAllInstances()

    #Get all instances over days old    
    oldinstances = OldInstances(instances, days)
    
    #Filter list by missing tags
    if len(oldinstances) > 0:
        missingInstances = findMissingTags(instances, mytags)
    else: 
        return 0
    
    #Get % Utilized from Id'ed systems
    if len(missingInstances) > 0:
        
        for missInstance in missingInstances:
            myr = None
            myr = IsCPUOver(5, missInstance.instance_id, days)
            if myr == None:
                #print("Control")
                tagAndPowerOff(missInstance)
