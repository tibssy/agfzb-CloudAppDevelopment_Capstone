const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {
    const dbName = "dealerships"
    const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY })
    const cloudant = CloudantV1.newInstance({
        authenticator: authenticator
        });
    cloudant.setServiceUrl(params.COUCH_URL);
    try {
        let dealerships = await cloudant.postFind({ db: dbName, selector:{state:params.state}});
        return { headers: { 'Content-Type': 'application/json' }, body: dealerships.result.docs }
    } catch (error) {
        return { error: error.description };
    }
}