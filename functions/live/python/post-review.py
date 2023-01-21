from ibmcloudant.cloudant_v1 import CloudantV1, Document
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException


def main(param_dict):
    db_name = "reviews"
    keyword = "review"
    print(param_dict['review'])
    try:
        authenticator = IAMAuthenticator(param_dict["IAM_API_KEY"])
        service = CloudantV1(authenticator=authenticator)
        service.set_service_url(param_dict["COUCH_URL"])

        if keyword in param_dict:
            doc = Document.from_dict(param_dict['review'])
            response = service.post_document(db=db_name, document=doc).get_result()
            return {"body": response}

    except ApiException as ae:
        if ("reason" in ae.http_response.json()):
            return {"error": ae.http_response.json()["reason"]}
        return {"status_code": ae.code, "error_message": ae.message}
