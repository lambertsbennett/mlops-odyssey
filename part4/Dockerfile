FROM python:3.8

RUN pip install mlflow psycopg2 boto3

EXPOSE 5000

ENTRYPOINT mlflow server \
        --default-artifact-root $ARTIFACT_STORE \
        --backend-store-uri postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_URL/$DB_NAME --host 0.0.0.0