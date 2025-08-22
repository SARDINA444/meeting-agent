import boto3
import json

class S3Backend:
    def __init__(self, bucket_name="pipeline-data"):
        self.s3 = boto3.client("s3", endpoint_url="http://minio:9000",
                               aws_access_key_id="minioadmin",
                               aws_secret_access_key="minioadmin")
        self.bucket = bucket_name
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except:
            self.s3.create_bucket(Bucket=self.bucket)

    def save_state(self, key: str, state: dict):
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(state).encode("utf-8"),
        )

    def load_state(self, key: str):
        try:
            obj = self.s3.get_object(Bucket=self.bucket, Key=key)
            return json.loads(obj["Body"].read().decode("utf-8"))
        except self.s3.exceptions.NoSuchKey:
            return None
