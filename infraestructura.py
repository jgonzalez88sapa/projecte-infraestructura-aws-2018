import boto3
import json
import time
import warnings
warnings.filterwarnings("ignore")
json_data = open('./infraestructura.json').read()
array = json.loads(json_data)
ec2 = boto3.resource('ec2', region_name='eu-west-1')
iam = boto3.client('iam')
s3 = boto3.resource('s3')

# IAM: Role
for role in array['role']:
    IamRole = iam.create_role(
        Path=role["Path"],
        RoleName=role["RoleName"],
        AssumeRolePolicyDocument=role["AssumeRolePolicyDocument"],
        Description=role["Description"],
        MaxSessionDuration=role["MaxSessionDuration"]
    )

    if role["InstanceProfileName"]:
        iam.create_instance_profile(
            InstanceProfileName=role["InstanceProfileName"],
            Path=role["Path"]
        )

        iam.add_role_to_instance_profile(
            InstanceProfileName=role["InstanceProfileName"],
            RoleName=role["RoleName"]
        )

    print('- Role:\t\t\t\t\t"' + role["RoleName"] + '" creat.')

# IAM: Polity to Role
for policy in array['policy']:
    iam.attach_role_policy(
        RoleName=policy['RoleName'],
        PolicyArn=policy['PolicyArn']
    )

# S3: Bucket
CreateBucket = 's3.create_bucket('
for key in array['s3']:
    if key == 'CreateBucketConfiguration':
        CreateBucket += "{}={{'LocationConstraint':'{}'}},".format(key, array['s3'][key]['LocationConstraint'])
    else:
        CreateBucket += "{}='{}',".format(key, array['s3'][key])
    if key == 'Bucket':
        S3BucketName = array['s3']['Bucket']
CreateBucket = CreateBucket[:-1]
CreateBucket += ')'
S3Bucket = eval(CreateBucket)
print('- Bucket:\t\t\t\t"' + S3BucketName + '" creat.')

# VPC
for network in array['vpc']:
    CreateVPC = 'ec2.create_vpc('
    VPCTags = 'vpc.create_tags(Tags=['
    for key in network.keys():
        if not (key == "tags"):
            CreateVPC += '{}=network["{}"],'.format(key, key)
        else:
            for tags in network[key]:
                VPCTags += json.dumps(tags, indent=0, sort_keys=True)
                VPCTags += ','
    CreateVPC = CreateVPC[:-1]
    CreateVPC += ')'
    VPCTags = VPCTags[:-1]
    VPCTags += '])'
    vpc = eval(CreateVPC)
    time.sleep(2)
    eval(VPCTags)
    print('- VPC:\t\t\t\t\t' + vpc.id + ' creada.')

# VPC: Subnets
for subnet in array['subnet']:
    x_pub = False
    CreateSubnet = 'ec2.create_subnet(VpcId="{}",'.format(vpc.id)
    SubnetTags = 'sb.create_tags(Tags=['
    for key in subnet.keys():
        if not (key == "tags"):
            if (key == "XarxaPublica") and (subnet[key]):
                x_pub = True
            else:
                CreateSubnet += '{}=subnet["{}"],'.format(key, key)
        else:
            for tags in subnet[key]:
                SubnetTags += json.dumps(tags, indent=0, sort_keys=True)
                SubnetTags += ','
    CreateSubnet = CreateSubnet[:-1]
    CreateSubnet += ')'
    SubnetTags = SubnetTags[:-1]
    SubnetTags += '])'
    sb = eval(CreateSubnet)
    time.sleep(2)
    eval(SubnetTags)
    print('- Subnet:\t\t\t\t' + sb.id + ' creada.')
    # Identify subnet for EC2 instances
    if x_pub:
        PublicSubnet = sb.id
    else:
        PrivateSubnet = sb.id
time.sleep(2)

# VPC: Internet Gateway
ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)

IGTags = 'ig.create_tags(Tags=['
for internetgateway in array['internet gateway']:
    for key in internetgateway.keys():
        for tags in internetgateway[key]:
            IGTags += json.dumps(tags, indent=0, sort_keys=True)
            IGTags += ','
IGTags = IGTags[:-1]
IGTags += '])'
eval(IGTags)
print('- Internet Gateway:\t\t' + ig.id + ' creat i adjuntat a ' + vpc.id + '.')

# VPC: Route Table attach Internet Gateway
RoutetTableIterator = vpc.route_tables.all()
for route_table in RoutetTableIterator:
    route = route_table.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=ig.id
    )

RouteTableTags = 'route_table.create_tags(Tags=['
for rt in array['route table']:
    for key in rt.keys():
        for tags in rt[key]:
            RouteTableTags += json.dumps(tags, indent=0, sort_keys=True)
            RouteTableTags += ','
RouteTableTags = RouteTableTags[:-1]
RouteTableTags += '])'
eval(RouteTableTags)
print('- Route Table:\t\t\t' + route_table.id + ' asignada a ' + ig.id + '.')

# VPC: Security Group
GroupName_ID = []
for sg in array['sg']:
    CreateSecurityGroup = "ec2.create_security_group(VpcId='{}',".format(vpc.id)
    for key in sg.keys():
        CreateSecurityGroup += '{}=sg["{}"],'.format(key, key)
    CreateSecurityGroup = CreateSecurityGroup[:-1]
    CreateSecurityGroup += ')'
    security_group = eval(CreateSecurityGroup)
    time.sleep(0.5)
    print('- Security Group:\t\t' + security_group.id + ' creat amb nom ' + security_group.group_name + '.')

    # Delete default Outbound Rules of the Security Groups
    security_group.revoke_egress(
        IpPermissions=[
            {
                'FromPort': 0,
                'ToPort': 65535,
                'IpProtocol': '-1',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                    }
                ]
            }
        ]
    )
    # Array to identify Security Group GroupName with the ID
    GroupName_ID += [sg["GroupName"], security_group.id]
Length_GN_ID = len(GroupName_ID)

# VPC: Security Groups Inbound Rules
for inbound in array['IN_SG']:
    for i in range(Length_GN_ID):
        if inbound['GroupName'] == GroupName_ID[i]:
            security_group = ec2.SecurityGroup(GroupName_ID[i+1])
            for key in inbound.keys():
                if key == 'IpRanges':
                    security_group.authorize_ingress(
                        IpPermissions=[
                            {
                                    'FromPort': inbound['FromPort'],
                                    'ToPort': inbound['ToPort'],
                                    'IpProtocol': inbound['IpProtocol'],
                                    'IpRanges': inbound['IpRanges']
                            }
                        ]
                    )
                if key == 'UserIdGroupPairs':
                    for j in range(Length_GN_ID):
                        if inbound['UserIdGroupPairs'][0]['GroupId'] == GroupName_ID[j]:
                            inbound['UserIdGroupPairs'][0]['GroupId'] = GroupName_ID[j+1]
                            break
                    security_group.authorize_ingress(
                        IpPermissions=[
                            {
                                'FromPort': inbound['FromPort'],
                                'ToPort': inbound['ToPort'],
                                'IpProtocol': inbound['IpProtocol'],
                                'UserIdGroupPairs': inbound['UserIdGroupPairs']
                            }
                        ]
                    )

# VPC: Security Groups Outbound Rules
for inbound in array['OUT_SG']:
    for i in range(Length_GN_ID):
        if inbound['GroupName'] == GroupName_ID[i]:
            security_group = ec2.SecurityGroup(GroupName_ID[i+1])
            for key in inbound.keys():
                if key == 'IpRanges':
                    security_group.authorize_egress(
                        IpPermissions=[
                            {
                                    'FromPort': inbound['FromPort'],
                                    'ToPort': inbound['ToPort'],
                                    'IpProtocol': inbound['IpProtocol'],
                                    'IpRanges': inbound['IpRanges']
                            }
                        ]
                    )
                if key == 'UserIdGroupPairs':
                    for j in range(Length_GN_ID):
                        if inbound['UserIdGroupPairs'][0]['GroupId'] == GroupName_ID[j]:
                            inbound['UserIdGroupPairs'][0]['GroupId'] = GroupName_ID[j+1]
                            break
                    security_group.authorize_egress(
                        IpPermissions=[
                            {
                                'FromPort': inbound['FromPort'],
                                'ToPort': inbound['ToPort'],
                                'IpProtocol': inbound['IpProtocol'],
                                'UserIdGroupPairs': inbound['UserIdGroupPairs']
                            }
                        ]
                    )

# EC2: Instances
for instance in array['ec2']:
    CreateInstance = 'ec2.create_instances('
    for key in instance.keys():
        if key == "NetworkInterfaces":
            CreateInstance += 'NetworkInterfaces=[{'
            for eth in instance[key]:
                AttachNetwork = ""
                for ethkey in eth:
                    if ethkey == "SubnetId":
                        if eth[ethkey] == "x_pub":
                            AttachNetwork += "'{}':'{}',".format(ethkey, PublicSubnet)
                            SubnetType = True  # Mark to identify kind of network
                        elif eth[ethkey] == "x_priv":
                            AttachNetwork += "'{}':'{}',".format(ethkey, PrivateSubnet)
                            SubnetType = False
                    elif ethkey == "Groups":
                        AttachNetwork += "'Groups':["
                        for group in eth[ethkey]:
                            for i in range(Length_GN_ID):
                                if GroupName_ID[i] == group:
                                    AttachNetwork += "'{}',".format(GroupName_ID[i+1])
                            AttachNetwork = AttachNetwork[:-1]
                            AttachNetwork += "],"
                    else:
                        AttachNetwork += "'{}':eth['{}'],".format(ethkey, ethkey)
                AttachNetwork = AttachNetwork[:-1]
                AttachNetwork += "}],"
                CreateInstance += AttachNetwork
        elif key == "UserData":
            Route = instance[key]
            Script = open(Route, 'rb').read()
            CreateInstance += 'UserData="{}",'.format(Script)
        else:
            CreateInstance += '{}=instance["{}"],'.format(key, key)
    CreateInstance = CreateInstance[:-1]
    CreateInstance += ')'
    EC2instance = eval(CreateInstance)

    for InstanceCreated in EC2instance:
        InstanceCreated.wait_until_running()
        InstanceCreated.reload()
        print('- EC2 Instance:\t\t\t' + InstanceCreated.id)
        if SubnetType:
            print("\t- Public IP:\t\t" + InstanceCreated.public_ip_address)
        print("\t- Subnet ID:\t\t" + InstanceCreated.subnet_id)
        print("\t- Private IP:\t\t" + InstanceCreated.private_ip_address)
