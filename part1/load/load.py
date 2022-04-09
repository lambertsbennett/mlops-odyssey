import yaml
from minio import Minio
from datetime import datetime


with open ("config.yaml", "r") as stream:
    config = yaml.safe_load(stream)


def put_file_minio(filename):
    client = Minio(
        "minio:9000",
        access_key=config["MINIO_USER"],
        secret_key=config["MINIO_PASSWORD"],
        secure=False
    )
    found = client.bucket_exists("openaq")
    if not found:
        client.make_bucket("openaq")
    else:
        print("Bucket 'openaq' already exists")

    client.fput_object(
        "openaq", f"{filename}", "/data.parquet", content_type="application/parquet"
    )
    print("File successfully uploaded!")  

if __name__ == '__main__':
    filename = f"data-{datetime.now().date()}.parquet"
    try:
        put_file_minio(filename)
    except Exception as e:
        print(e)
