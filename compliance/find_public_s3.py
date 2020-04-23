import argparse
import sys
import csv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M "
    )

try:
  import boto3
except ImportError:
  print("boto3 package is missing. Please install by running pip3 install boto3")

try:
  from botocore import session
except ImportError:
  print("botocore pacakge not found. Please install by running pip3 install botocore")

def get_s3_session(profile):
    """
    Return s3 session for that account
    """
    session = boto3.Session(profile_name=profile)
    return session.client('s3') 

def get_all_profiles():
    """
    Return a list of all AWS profiles
    """
    s = session.Session()
    return s.available_profiles

    
def get_public_buckets(s3, buckets, account):
    """Parses all the s3 buckets in a given  AWS account and returns all the public s3 buckets with their level of permission"""
    result = []
    for b in buckets:
       g_id = None
       name = b['Name']
       response = s3.get_bucket_acl(Bucket=name)
       grants = response["Grants"]
       access = []
       for grant in grants:
          grantee = grant["Grantee"]
          if "URI" in grantee:
              g_id = grantee["URI"].split("/")[-1]
              access.append(grant["Permission"])
       if g_id == "AllUsers":
           result.append({"Bucket" : name, "Permissons" : ", ".join(x for x in access), "Account": account})
    return result


def generate_report(blist,outfile="public_buckets.csv"):
    """
    Generate a csv report of the public buckets with the account and permission details
    """
    fieldnames = blist[0].keys()
    with open(outfile,'w',newline='') as report:
      csvwriter = csv.DictWriter(report,fieldnames=fieldnames)
      csvwriter.writeheader()
      csvwriter.writerows(blist)

if __name__ == "__main__":


    usage = "python3 find_public_s3.py [--account ACCOUNT_NAME] -all"
    parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description="""Script to parse all s3 buckets within an account or multiple accounts and generates a csv report detailing the public buckets, level of access. S3 buckets can have following access : 
            - READ Allows any user to list objects in bucket
            - WRITE Allows any user to create, overwrite, delete any objects in bucket
            - READ_ACP Allows any user to read bucket ACL
            - WRITE_ACP Allows any user to write bucket ACL
            - FULL_CONTROL Allows any user to Read, Write, READ_ACP, WRITE_ACP permissions on the bucket
              """,
              usage=usage)
    parser.add_argument(
        '--profile',
        dest="profile",
        default="default",
        required=False,
        help="AWS profile name defined in the credentials configuration")
    parser.add_argument(
         '--all',
         dest="all",
         action='store_true',
         help="Parse all AWS profiles from shared credentials file (~/aws/credentials) for public s3 buckets, omit --profile flag when using this flag",
         required=False,
         default=False)

    if len(sys.argv) < 2:
      parser.print_help()
      exit(1)

    args = parser.parse_args()

    pbuckets = []

    if args.all:
      accounts = get_all_profiles()
      for account in accounts:
          logging.info(f"Parsing AWS account {account}")
          s3 = get_s3_session(account)
          allbuckets = s3.list_buckets()['Buckets']
          pbuckets.extend(get_public_buckets(s3,allbuckets, account))
      logging.info("Finished parsing all AWS accounts")
    elif args.profile:
      s3 = get_s3_session(args.profile)
      allbuckets = s3.list_buckets()['Buckets']
      pbuckets.extend(get_public_buckets(s3,allbuckets, args.profile))

    logging.info("Generating csv report of all identified public buckets")
    generate_report(pbuckets,"public_buckets.csv")



