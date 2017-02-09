from troposphere import Ref, Template
import troposphere.ec2 as ec2
from troposphere.ecs import Cluster, ContainerDefinition, TaskDefinition, Service, LoadBalancer, PortMapping, Environment
from troposphere.autoscaling import LaunchConfiguration
from troposphere import Base64, Join
from troposphere.autoscaling import AutoScalingGroup, Metadata
from troposphere.elasticloadbalancing import LoadBalancer as ELBLoadBalancer


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
                                             IamInstanceProfile=Ref(
                                                 'DemoInstanceProfile'),
                                             InstanceType='t2.medium',
                                             AssociatePublicIpAddress='true',
                                             ))

demo_asg = t.add_resource(AutoScalingGroup(
    'DemoAsg',
    DesiredCapacity='2',
    MinSize='2',
    MaxSize='2',
    VPCZoneIdentifier=['subnet-0dc03a7a', 'subnet-5170d434'],
    # AvailabilityZones=[],
    LaunchConfigurationName=Ref('DemoLc'),
))

demo_cd = ContainerDefinition(
    Image='725827686899.dkr.ecr.us-west-2.amazonaws.com/arun/docker/demo_svc:latest', 
    Name='demo-lb-containername', 
    Memory=128,
    Environment=[Environment(Name='PORT', Value='9000')],
    PortMappings=[PortMapping(ContainerPort=9000, HostPort=9000)])  # all these are required or an alternative for each attribute

demo_td = t.add_resource(TaskDefinition("DemoTD", ContainerDefinitions=[
                         demo_cd], Family='demo-ecsdemo_svc'))

demo_elb_lb = ELBLoadBalancer('DemoElbLb2', Listeners=[
    {
        "InstancePort": "9000",
        "LoadBalancerPort": "80",
        "Protocol": "TCP",
        "InstanceProtocol": "TCP"
    }
], LoadBalancerName='DemoElbLb2', Subnets=['subnet-0dc03a7a', 'subnet-5170d434'],)


t.add_resource(demo_elb_lb)

demo_lb = LoadBalancer('DemoLB', ContainerPort='9000',
                       ContainerName='demo-lb-containername', LoadBalancerName='DemoElbLb2')

#t.add_resource(demo_lb)


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
t.add_resource(Service('DemoService', TaskDefinition=Ref('DemoTD'), Cluster=Ref(
    'DemoCluster'), Role=Ref('DemoServiceRole'), DesiredCount=2, LoadBalancers=[demo_lb]))

print(t.to_json())
