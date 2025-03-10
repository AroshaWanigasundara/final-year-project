const { Requester, Validator } = require('@chainlink/external-adapter')
const axios = require('axios');
const fs = require('fs');
const { Web3Storage, getFilesFromPath } = require('web3.storage');
const minimist = require('minimist');

// Define custom error scenarios for the API.
// Return true for the adapter to retry.
const customError = (data) => {
  if (data.Response === 'Error') return true
  return false
}

// Define custom parameters to be used by the adapter.
// Extra parameters can be stated in the extra object,
// with a Boolean value indicating whether or not they
// should be required.
const customParams = {
  cid: ['cid', 'contentIdentifier'],
  endpoint: false
}

function calculateMedian(arrays) {
  const resultArray = [];

  // Loop through each element in the arrays
  for (let i = 0; i < arrays[0].length; i++) {
    const elements = [];

    // Loop through each array to get the ith element from each array
    for (const array of arrays) {
      elements.push(array[i]);
    }

    // Sort the elements in ascending order
    elements.sort((a, b) => a - b);

    // Calculate the median based on the number of elements
    const mid = Math.floor(elements.length / 2);
    const median =
      elements.length % 2 === 0
        ? ((elements[mid - 1] + elements[mid]) / 2)*elements.length
        : (elements[mid])*elements.length;

    // Add the median value to the result array
    resultArray.push(median);
  }

  return resultArray;
}

async function store_data () {
  const args = minimist(process.argv.slice(2))
  //const token = args.token
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweDRmRkNCMTBFREQyZEYyMzFFODE2YjZGNGZCMkE0MzU4NjM4OGI3ZjQiLCJpc3MiOiJ3ZWIzLXN0b3JhZ2UiLCJpYXQiOjE2ODcxOTI1Nzg1ODAsIm5hbWUiOiJGTFN5c3RlbSJ9.aSh7AiqP8V7a6qDAX7xmdlppY9QPX-12A-pTUSME3TM'
  //const path = './web3-storage-quickstart/' + client + '.txt'
  const path = './iteration.txt'
  if (!token) {
    return console.error('A token is needed. You can create one on https://web3.storage')
  }

  const storage = new Web3Storage({ token })
  const files = []
  const pathFiles = await getFilesFromPath(path)
  files.push(...pathFiles)

  //console.log(`Uploading ${files.length} files`)
  const cid = await storage.put(files)
  console.log(cid)
  return cid;
}

async function createRequest (input, callback) {

  const weightList = [];
  const validator = new Validator(callback, input, customParams);
  const jobRunID = validator.validated.id;
  //const endpoint = validator.validated.data.endpoint || 'weights';
  const cid = validator.validated.data.cid;
  // The Validator helps you validate the Chainlink request data

  try {
    await Promise.all(
      Array.from({ length: 10 }, (_, i) => i + 1).map(async (i) => {
        const fileUrl = `https://${cid}.ipfs.w3s.link/clients_model/clients_${i}.txt`;
        const response = await axios.get(fileUrl);
        const content = response.data;
        weightList.push(content);
      })
    );

    // Once all the Axios requests are completed, calculate the median
    const resultsArray = calculateMedian(weightList);

    const fileContent = JSON.stringify(resultsArray);
    const filePath = './iteration.txt';
    fs.writeFileSync(filePath, fileContent);
    console.log('successfully created median array');

    const message = await store_data();
    //message = "bafybeihx5helaqnfprofgyhvqnpzk45g6kxjbugu437cwthm6bsky6r7km"

    //message.result = (message, ['message'])
    //callback(response.status, Requester.success(jobRunID, response))

    callback(200, {
      "id": jobRunID,
      "data": message,
    });
  } catch (error) {
    console.error('Error:', error.message);
    callback(500, Requester.errored(jobRunID, error));
  }
};

// This is a wrapper to allow the function to work with
// GCP Functions
exports.gcpservice = (req, res) => {
  createRequest(req.body, (statusCode, data) => {
    res.status(statusCode).send(data)
  })
}

// This is a wrapper to allow the function to work with
// AWS Lambda
exports.handler = (event, context, callback) => {
  createRequest(event, (statusCode, data) => {
    callback(null, data)
  })
}

// This is a wrapper to allow the function to work with
// newer AWS Lambda implementations
exports.handlerv2 = (event, context, callback) => {
  createRequest(JSON.parse(event.body), (statusCode, data) => {
    callback(null, {
      statusCode: statusCode,
      body: JSON.stringify(data),
      isBase64Encoded: false
    })
  })
}

// This allows the function to be exported for testing
// or for running in express
module.exports.createRequest = createRequest
