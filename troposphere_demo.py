from troposphere import Ref, Template
import troposphere.ec2 as ec2
from troposphere.ecs import Cluster
from troposphere.autoscaling import LaunchConfiguration
from troposphere import Base64, Join
from troposphere.autoscaling import AutoScalingGroup, Metadata

from troposphere.iam import InstanceProfile
from troposphere.iam import Role

t = Template()

demo_cluster_role = t.add_resource(Role(
    'DemoClusterRole',
    Path='/',
    ManagedPolicyArns=[
        'arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role'
    ],
    AssumeRolePolicyDocument={'Version': '2012-10-17',
                              'Statement': [{'Action': 'sts:AssumeRole',
                                             'Principal':
                                             {'Service': 'ec2.amazonaws.com'},
                                             'Effect': 'Allow',
                                             }]}
))

demo_instance_profile = t.add_resource(InstanceProfile(
    'DemoInstanceProfile',
    Path='/',
    Roles=[Ref('DemoClusterRole')],
))


demo_cluster = t.add_resource(Cluster('DemoCluster',))


demo_lc = t.add_resource(LaunchConfiguration('DemoLc',
    UserData=Base64(Join('',
                        ["",
                "#!/bin/bash\n",
                "echo ECS_CLUSTER=",
                {
                  "Ref": "DemoCluster"
                },
                " >> /etc/ecs/ecs.config\n"
                ]
                        )),
    ImageId='ami-5b6dde3b',
    KeyName='ecs-demo',
    SecurityGroups=['sg-bed64ddb'],
    IamInstanceProfile=Ref('DemoInstanceProfile'),
    InstanceType='t2.medium',
    AssociatePublicIpAddress='true',
))

demo_asg = t.add_resource(AutoScalingGroup(
    'DemoAsg',
    DesiredCapacity='2',
    MinSize='2',
    MaxSize='2',
    VPCZoneIdentifier=['subnet-0dc03a7a', 'subnet-5170d434'],
    #AvailabilityZones=[],
    LaunchConfigurationName=Ref('DemoLc'),
))


print(t.to_json())