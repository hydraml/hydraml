import os
import sys
import boto3
import json

import numpy as np


def get_model():
    bucket = boto3.resource('s3').Bucket("{}".format(os.environ.get('bucket_name')))
    model = bucket.Object("{}".format(os.environ.get('model_name'))).get()
    return model


def has_predict(model):
    return hasattr(model, predict)


def configure_input(input_data):
    pass


def configure_response(prediction):
    pass


def get_param(event, param):
    params = event["queryStringParameters"]
    return params[param]


def gateway_response(code, body):
    return {"status": code, "response": json.dumps(body)}


def predict(event, context):
    model = get_model()
    if not has_predict(model):
        raise AttributeError("supplied model does not have a predict function")

    try:
        data = get_param(event, 'data')
        data = configure_input(data)
        predictions = model.predict(data)
    except Exception as e:
        err = {"error_message": "prediction or data manipulation failed",
               "stack_trace": e}
        return gateway_response(503, err)

    return gateway_response(200, configure_response(predictions))
