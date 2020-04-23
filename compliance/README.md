##Scripts to identify resources which maybe violating compliance requirements. 

### Identify public s3 buckets 
Identify and report all the public s3 buckets in an account with their level of access. 

#### Usage 

```
usage: python3 find_public_s3.py [--account ACCOUNT_NAME] -all

Script that parses all s3 buckets within an account or all accounts and lists all the public buckets with their access permissions. Public buckets can have following access : 
            - READ Allows any user to list objects in bucket
            - WRITE Allows any user to create, overwrite, delete any objects in bucket
            - READ_ACP Allows any user to read bucket ACL
            - WRITE_ACP Allows any user to write bucket ACL
            - FULL_CONTROL Allows any user to Read, Write, READ_ACP, WRITE_ACP permissions on the bucket

```


### Requirements : 
- Python3 3.7.3
- boto3==1.9.183                                                                                                           
- botocore==1.12.183