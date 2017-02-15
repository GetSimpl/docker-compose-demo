from troposphere import Ref, Template
from troposphere.ecs import (Cluster,
                             ContainerDefinition,
                             TaskDefinition,
                             Service,
                             LoadBalancer,
                             PortMapping,
                             Environment
                             )
from troposphere.autoscaling import LaunchConfiguration
from troposphere import Base64, Join, GetAtt
from troposphere.autoscaling import AutoScalingGroup
from troposphere.elasticloadbalancing import LoadBalancer as ELBLoadBalancer


from troposphere.iam import InstanceProfile
from troposphere.iam import Role

t = Template()

# create a role to be able to create a cluster
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

# create an instance profile with the above role
demo_instance_profile = t.add_resource(InstanceProfile(
    'DemoInstanceProfile',
    Path='/',
    Roles=[Ref('DemoClusterRole')],
))


demo_cluster = t.add_resource(Cluster('DemoCluster',))

# create a launch configuraton
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
                                             IamInstanceProfile=Ref(
                                                 'DemoInstanceProfile'),
                                             InstanceType='t2.nano',
                                             AssociatePublicIpAddress='true',
                                             ))

# create an auto scaling group for all the EC2 instances
demo_asg = t.add_resource(AutoScalingGroup(
    'DemoAsg',
    DesiredCapacity='2',
    MinSize='2',
    MaxSize='4',
    VPCZoneIdentifier=['subnet-0dc03a7a', 'subnet-5170d434'],
    # AvailabilityZones=[],
    LaunchConfigurationName=Ref('DemoLc'),
))

#  create a container definition for demo service
demo_cd_svc = ContainerDefinition(
    Image='725827686899.dkr.ecr.us-west-2.amazonaws.com/arun/docker/demo_svc:latest',
    Name='demo-lb-containername',
    Cpu=1024,
    Memory=128,
    Environment=[Environment(Name='PORT', Value='9000')],
    PortMappings=[PortMapping(ContainerPort=9000, HostPort=9000)])  # all these are required or an alternative for each attribute

# create a task definition for demo service
demo_td = t.add_resource(TaskDefinition("DemoTD", ContainerDefinitions=[
                         demo_cd_svc], Family='demo-ecsdemo_svc'))

# create an elb for demo service
demo_elb_lb = ELBLoadBalancer('DemoElb', Listeners=[
    {
        "InstancePort": "9000",
        "LoadBalancerPort": "80",
        "Protocol": "TCP",
        "InstanceProtocol": "TCP"
    }
], LoadBalancerName='DemoElb', Subnets=['subnet-0dc03a7a', 'subnet-5170d434'],)
t.add_resource(demo_elb_lb)

# attach it to service
demo_lb = LoadBalancer('DemoLB', ContainerPort='9000',
                       ContainerName='demo-lb-containername', LoadBalancerName='DemoElb')

# create a service role
demo_service_role = t.add_resource(Role(
    'DemoServiceRole',
    Path='/',
    ManagedPolicyArns=[
        'arn:aws:iam::aws:policy/AmazonEC2ContainerServiceFullAccess',
    ],
    AssumeRolePolicyDocument={'Version': '2012-10-17',
                              'Statement': [{'Action': 'sts:AssumeRole',
                                             'Principal':
                                             {'Service': 'ecs.amazonaws.com'},
                                             'Effect': 'Allow',
                                             }]}
))

# create a service for demo service
t.add_resource(Service('DemoService', TaskDefinition=Ref('DemoTD'), Cluster=Ref(
    'DemoCluster'), Role=Ref('DemoServiceRole'), DesiredCount=1, LoadBalancers=[demo_lb]))


#  create a container definition for demo UI
demo_cd_ui = ContainerDefinition(
    Image='725827686899.dkr.ecr.us-west-2.amazonaws.com/arun/docker/demo_ui:latest',
    Name='demo-lb-ui-containername',
    Memory=128,
    Cpu=1024,
    Environment=[
        Environment(Name='SERVICE_URI_PORT', Value='80'),
        Environment(Name='SERVICE_URI_HOST', Value=GetAtt('DemoElb', 'DNSName'))
        ],
    #demo-lb-containername
    PortMappings=[PortMapping(ContainerPort=8080, HostPort=80)])  # all these are required or an alternative for each attribute

# create a task definition for demo UI
demo_td_ui = t.add_resource(TaskDefinition("DemoTdUi", ContainerDefinitions=[
                         demo_cd_ui], Family='demo-ecsdemo_ui'))


# create an elb for demo UI
demo_elb_lb_ui = ELBLoadBalancer('DemoElbLbUi', Listeners=[
    {
        "InstancePort": "80",
        "LoadBalancerPort": "80",
        "Protocol": "TCP",
        "InstanceProtocol": "TCP"
    }
], LoadBalancerName='DemoElbLbUi', Subnets=['subnet-0dc03a7a', 'subnet-5170d434'],)
t.add_resource(demo_elb_lb_ui)

# attach it to service for UI
demo_lb_ui = LoadBalancer('DemoLBUi', ContainerPort='8080',
                       ContainerName='demo-lb-ui-containername', LoadBalancerName='DemoElbLbUi')

# create a service role for UI
demo_service_role = t.add_resource(Role(
    'DemoServiceRoleUi',
    Path='/',
    ManagedPolicyArns=[
        'arn:aws:iam::aws:policy/AmazonEC2ContainerServiceFullAccess',
    ],
    AssumeRolePolicyDocument={'Version': '2012-10-17',
                              'Statement': [{'Action': 'sts:AssumeRole',
                                             'Principal':
                                             {'Service': 'ecs.amazonaws.com'},
                                             'Effect': 'Allow',
                                             }]}
))

# create a service for demo UI
t.add_resource(Service('DemoUI', TaskDefinition=Ref('DemoTdUi'), Cluster=Ref(
    'DemoCluster'), Role=Ref('DemoServiceRoleUi'), DesiredCount=1, LoadBalancers=[demo_lb_ui]))


print(t.to_json())
