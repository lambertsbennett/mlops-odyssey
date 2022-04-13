import profile
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService
from hera.artifact import InputArtifact, OutputArtifact

TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjRvbjlyZnVxbDNUaDNVWm9QLTdZbTY2RThMYUd5Yjdzc2lDMFlUU0pjNXMifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJhcmdvIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImFyZ28tdG9rZW4teHp6Z2siLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiYXJnbyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImIwOTkyZDllLWVkNTMtNGZiMS04ZTM4LTQ2MGNjZWUyMzM0NSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDphcmdvOmFyZ28ifQ.BS1DEcSA90GiiyL8TbbT40JwS-909cIJa8N3DybfGyJVrD04tsWPoDlDFPmt2ENkHfQ4hMnw7wuDj59cHhpWIoCthwsoMNGY3oKDMgUcqrEu-7fyIlt53R3yRT_7aekqQF-eQbKGVrlUVL-GsDf7pmFte-osBPJdB-A44O8_b70qDNqy1daTlY_HRiTXFKBJV3bZyl1M0RnRFuwY4JADCu9nxzcAFOKl1oP2ffJCEjlSGY0bknpH8Wr462v6lPbHeM5OY1bIqN3mD98V0NsmyDzkUNa_efE0lwFVXFmO08O6vH7erT_Pcxj-og3AwluIWaM-cFeUfLdM76n6CBAY9g"


def extract():
    import requests
    from datetime import datetime, timedelta
    import pandas as pd
    
    # OpenAQ base URL.
    BASE_URL = "https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com"


    def healthy_connection():
        r = requests.get(f"{BASE_URL}/ping")
        if r.status_code == 200:
            return True
        else:
            return False
    

    # Get historical data for Vienna 
    def get_historical_data(start, end, data_category="pm25", all=False, limit=10000):
        if all:
            params = {"country":"AT", "city": "Wien", "date_from": start, "date_to": end, "limit": limit}
            r = requests.get(f"{BASE_URL}/v2/measurements", params=params)
            response_data = r.json()["results"]

        else:
            params = {"country":"AT", "city": "Wien", "parameter": data_category, "date_from": start, "date_to": end, "limit": limit}
            r = requests.get(f"{BASE_URL}/v2/measurements", params=params)
            response_data = r.json()["results"]
        
        return response_data
    


    current_date = datetime.now()
    previous_date = current_date - timedelta(days=100)
    
    if healthy_connection():
        r = get_historical_data(previous_date.date(), current_date.date(), all=True, limit=10000)
    else:
        raise Exception("Could not connect to OpenAQ API.")

    df = pd.json_normalize(r)
    df.to_csv("/data/raw_data.csv")


def generate_expectations():
    from great_expectations.data_context.types.base import DataContextConfig, DatasourceConfig, FilesystemStoreBackendDefaults
    from great_expectations.data_context import BaseDataContext
    from great_expectations.core.batch import RuntimeBatchRequest
    from great_expectations.profile.user_configurable_profiler import UserConfigurableProfiler
    from minio import Minio
    import tarfile
    import os.path
    
    data_context_config = DataContextConfig(
        datasources={
            "pandas": DatasourceConfig(
                class_name="Datasource",
                execution_engine={
                    "class_name": "PandasExecutionEngine"
                },
                data_connectors={
                    "faker_data": {
                        "class_name": "ConfiguredAssetFilesystemDataConnector",
                        "base_directory": "/data",
                        "assets": {
                            "faker_data": {
                                "pattern": r"(.*)",
                                "group_names": ["data_asset"]
                            }
                        },
                    }
                },
            )
        },
        store_backend_defaults=FilesystemStoreBackendDefaults(root_directory="/ge-store"),
    )

    context = BaseDataContext(project_config=data_context_config)

    datasource_config = {
        "name": "raw_data",
        "class_name": "Datasource",
        "module_name": "great_expectations.datasource",
        "execution_engine": {
            "module_name": "great_expectations.execution_engine",
            "class_name": "PandasExecutionEngine",
        },
        "data_connectors": {
            "default_runtime_data_connector_name": {
                "class_name": "RuntimeDataConnector",
                "module_name": "great_expectations.datasource.data_connector",
                "batch_identifiers": ["default_identifier_name"],
            },
            "default_inferred_data_connector_name": {
                "class_name": "InferredAssetFilesystemDataConnector",
                "base_directory": "/data/",
                "default_regex": {"group_names": ["data_asset_name"], "pattern": "(.*)"},
            },
        },
    }

    context.add_datasource(**datasource_config)

    context.create_expectation_suite(
        expectation_suite_name="default_suite", overwrite_existing=True
    )

    batch_request = RuntimeBatchRequest(
        datasource_name="raw_data",
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name="test",  # This can be anything that identifies this data_asset for you
        runtime_parameters={"path": "./data/raw_data.csv"},  # Add your path here.
        batch_identifiers={"default_identifier_name": "default_identifier"},
    )

    validator = context.get_validator(
        batch_request=batch_request, expectation_suite_name="default_suite"
    )

    profiler = UserConfigurableProfiler(
        profile_dataset=validator,
        excluded_expectations=None,
        ignored_columns=None,
        not_null_only=False,
        primary_or_compound_key=False,
        semantic_types_dict=None,
        table_expectations_only=False,
        value_set_threshold="MANY"
    )

    suite = profiler.build_suite()

    validator.save_expectation_suite(discard_failed_expectations=False)

    # Create a tar.gz of the great expectations directory
    with tarfile.open("ge-store.tar.gz", "w:gz") as tar:
        tar.add("/ge-store", arcname=os.path.basename("/ge-store"))

    # Save the zip archive to Minio
    client = Minio(
        "minio.mlops:9000",
        access_key="admin",
        secret_key="uFjMGBwTmS",
        secure=False
    )

    client.fput_object(
        "validation", "ge-store.tar.gz", "./ge-store.tar.gz",
    )


ws = WorkflowService(host="https://localhost:2746", verify_ssl=False, token=TOKEN)
w = Workflow("generate-expectations", ws, namespace="argo")

extract_task = Task("extract-openaq", extract, image="lambertsbennett/extract:v2", 
                    output_artifacts = [OutputArtifact(name="RawData", path="/data/raw_data.csv")])

ge_task = Task("great-expectations-gen", generate_expectations, image="lambertsbennett/argo-ge:v1", 
                    input_artifacts = [InputArtifact(name="RawData", path="/data/raw_data.csv", from_task="extract-openaq", artifact_name="RawData")])

extract_task >> ge_task

w.add_tasks(extract_task, ge_task)
w.submit()