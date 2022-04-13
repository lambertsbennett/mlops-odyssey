from seldon_core.seldon_client import SeldonClient

sc = SeldonClient(gateway="ambassador", transport="rest", deployment_name="mlflow-serving-default-0-regressor", namespace="models", gateway_endpoint="localhost:80", microservice_endpoint="localhost/model/", debug=True, ssl=False)

r = sc.predict()

print(r)