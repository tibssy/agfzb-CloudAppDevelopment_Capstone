const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {
    const dbName = "dealerships"
    const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY })
    const cloudant = CloudantV1.newInstance({
        authenticator: authenticator
        });
    cloudant.setServiceUrl(params.COUCH_URL);
    let selector = (params.state) ? {state:params.state} : (params.dealerId) ? {id:parseInt(params.dealerId)} : {};
    console.log(selector)
    try {
        let dealerships = await cloudant.postFind({ db: dbName, selector:selector});
        return { headers: { 'Content-Type': 'application/json' }, body: dealerships.result.docs }
    } catch (error) {
        return { error: error.description };
    }
}