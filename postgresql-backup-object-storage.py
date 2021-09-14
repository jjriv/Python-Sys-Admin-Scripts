#!/usr/bin/python3

import ibm_boto3
from ibm_botocore.client import Config, ClientError
import math
import datetime
import smtplib

#Constants for IBM COS values
#public endpoint (dev)
#COS_ENDPOINT = "----"
#private endpoint (production)
COS_ENDPOINT = "---"
#api key for dev
#COS_API_KEY_ID = "---"
#api key for production
COS_API_KEY_ID = "---"
#resource instance id for dev
#COS_INSTANCE_CRN = "---"
#resource instance id for production
COS_INSTANCE_CRN = "---"

dirnum = str(int(math.floor(int(datetime.datetime.now().strftime("%s")) / 86400) % 3))
yesterday = datetime.date.today() - datetime.timedelta(1)
isodate = yesterday.strftime("%Y-%m-%d")
dbfiles = [
        "base.tar.gz",
        "pg_wal.tar.gz",
        ]
#manual override
#dirnum = "2"
#isodate = "2021-09-10"


# Create resource
cos = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

def upload_large_file(bucket_name, item_name, file_path):
    umsg = "Starting large file upload for {0} to bucket: {1}\n".format(item_name, bucket_name)

    # set the chunk size to 20 MB
    part_size = 1024 * 1024 * 20

    # set threadhold to 20 MB
    file_threshold = 1024 * 1024 * 20

    # set the transfer threshold and chunk size in config settings
    transfer_config = ibm_boto3.s3.transfer.TransferConfig(
        multipart_threshold=file_threshold,
        multipart_chunksize=part_size
    )

    # create transfer manager
    transfer_mgr = ibm_boto3.s3.transfer.TransferManager(cos, config=transfer_config)
    
    try:
        # initiate file upload
        future = transfer_mgr.upload(file_path, bucket_name, item_name)

        # wait for upload to complete
        future.result()

        umsg += "Large file upload complete!\n"
    except Exception as e:
        umsg += "Unable to complete large file upload: {0}\n".format(e)
    finally:
        transfer_mgr.shutdown()
        return umsg

res = ''
for dbfile in dbfiles:
    res += upload_large_file('backup-production', isodate + '/' + dbfile + '.gpg', '/backup/' + dirnum + '/' + dbfile + '.gpg')

msg = "From: backup@pelagodesign.com\r\n"
msg = msg + "To: jreeve@pelagodesign.com\r\n"
msg = msg + "Subject: Production: DB Backup to Object Storage\r\n"
msg = msg + "\r\n"
msg = msg + res + "\n"

server = smtplib.SMTP("localhost")
server.sendmail("backup@pelagodesign.com", "jreeve@pelagodesign.com", msg.encode("utf-8"))
server.quit()
