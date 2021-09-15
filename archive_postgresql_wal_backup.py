#!/usr/bin/python

import ibm_boto3
from ibm_botocore.client import Config, ClientError
import os
import datetime

#Constants for IBM COS values
#private endpoint (production)
COS_ENDPOINT = "---"
#api key for production
COS_API_KEY_ID = "---"
#resource instance id for production
COS_INSTANCE_CRN = "---"

bucket = 'backup-production'
objpre = 'wal/'
path = '/postgresql_wal_backup/wal'
hoursoverlap = 6
timeoverlap = datetime.datetime.now() - datetime.timedelta(hours=hoursoverlap)

#cos client
cos = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

def get_item_info(bucket_name, item_name):
    try:
        objhead = cos.head_object(
            Bucket = bucket_name,
            Key = item_name)
        return objhead['ContentLength']
    except ClientError as be:
        return 0
    except Exception as e:
        return 0
        
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

#pull a list of wal files
walfiles = sorted(os.listdir(path))

#check to see if each one exists
for wal in walfiles:
    ctimedt = datetime.datetime.fromtimestamp(os.stat(path + '/' + wal).st_ctime)
    #only upload files from last 12 hours to avoid repeated checks of older wal
    if ctimedt < timeoverlap:
        msg = "Skip: " + wal
        print(msg)
        continue
    if get_item_info(bucket, objpre + wal) == 0:
        msg = upload_large_file(bucket, objpre + wal, path + "/" + wal)
    else:
        msg = "Exists: " + wal
    print(msg)
    #quit()

