#!/bin/bash
echo "$(date +'%D-%T') INFO: Configuring workspace"
ecs-cli configure --region ap-southeast-1 --access-key AKIAJLIGFC54Q6P4ZQ3A --secret-key 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 --cluster 'stage-ecs-api' --compose-project-name-prefix '' --compose-service-name-prefix  '' --cfn-stack-name-prefix ''

echo "$(date +'%D-%T') INFO: Creating security Group"
sgid=$(aws ec2 create-security-group --group-name ecscli-api-sg --description "Staging ECS API Services" --vpc-id vpc-32b25857 | grep GroupId | grep -v grep | awk -F ":" '{print $2}' | sed s/\"//g)
aws ec2 authorize-security-group-ingress --group-id $sgid --protocol tcp --port 80  --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $sgid --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $sgid --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $sgid --protocol all --port all --cidr 172.31.0.0/16
echo "$(date +'%D-%T') INFO: Created security group $sgid witl all rules"
echo "$(date +'%D-%T') INFO: setting up cluster"
ecs-cli up --keypair zookeeper --capability-iam --size 2  --security-group $sgid --port 80 --subnets subnet-8be80ffc,subnet-d4ee2eb1 --vpc vpc-32b25857 --instance-type t2.medium

echo "$(date +'%D-%T') INFO: Creating task from compose file "
ecs-cli compose --file api.yml up

echo "$(date +'%D-%T') INFO: Disributing the task to instances "
ecs-cli compose --file api.yml scale 2

echo "$(date +'%D-%T') INFO: Setting up Services"
ecs-cli compose --file api.yml down

#te elb & add a dns CNAME for the elb dns
echo "$(date +'%D-%T') INFO: Setting up ELB"
aws elb create-load-balancer --load-balancer-name "stage-ecs-api-elb" --listeners Protocol="TCP,LoadBalancerPort=80,InstanceProtocol=TCP,InstancePort=80" --subnets "subnet-d4ee2eb1" "
subnet-8be80ffc" --security-groups "sg-7c77c11b"

# create service with above created task definition & elb

echo "$(date +'%D-%T') INFO: Adding ECS Cluster to ELB"
aws ecs create-service --service-name "stage-ecs-api-service" --cluster "stage-ecs-api" --task-definition "api" --load-balancers "loadBalancerName=stage-ecs-api-elb,containerName=api,containerPort=80" --desired-count 2 --deployment-configuration "maximumPercent=200,minimumHealthyPercent=50" --role ecsServiceRole
#ecs-cli compose --file api.yml service up
#ecs-cli compose --file api.yml scale 2