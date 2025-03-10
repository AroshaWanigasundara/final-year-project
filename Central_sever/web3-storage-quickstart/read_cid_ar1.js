import Web3 from 'web3';
import fs from 'fs';

const web3 = new Web3('https://sepolia.infura.io/v3/edbaf363f322439e9b71df83782130d1'); // Replace with your Infura project ID or provide your own Ethereum node URL

//const contractAddress = '0x13F790e006804B3e643db9A09EFd49Cb99f1a98D'; // Replace with your smart contract address
const contractAddress = '0x9d78ddd16A84271D7B5e48e7e058F2B18E619F6F'

const abi = JSON.parse(fs.readFileSync('./web3-storage-quickstart/oracle_contract_abi.json'));
//const abi = JSON.parse(fs.readFileSync('./oracle_contract_abi.json'));

const contract = new web3.eth.Contract(abi, contractAddress);

let datarequest = true;

async function getContractTransactions() {
  try {
    const events = await contract.getPastEvents('allEvents', { fromBlock: 0, toBlock: 'latest' });

    for (let i = (events.length - 1); (events.length - 2) < i ; i--) {
      const transaction = await web3.eth.getTransaction(events[i].transactionHash);
      //console.log('----------------------------------');
      const inputData = transaction.data.slice(10); // Remove the function signature from the input data
      let aggregatCid = utf8Decode(inputData).slice(236);
      let aggregationCid = aggregatCid.slice(-64);
      aggregationCid = aggregationCid.slice(0,59);
      if(typeof aggregationCid === "string" && aggregationCid.length!==0){
        datarequest = false;
        console.log(aggregationCid);
        break
      }
      //console.log(aggregationCid);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}


function utf8Decode(hexString) {
    // Convert hexadecimal string to binary
    const binaryString = hexString.match(/.{1,2}/g).map(hex => parseInt(hex, 16).toString(2).padStart(8, '0')).join('');
  
    let decodedString = '';
    let i = 0;
  
    while (i < binaryString.length) {
      const leadingOnes = getLeadingOnes(binaryString[i]);
  
      // Determine the number of bytes for the character based on the leading '1' bits
      const byteCount = leadingOnes + 1;
  
      // Extract the code point from the binary string
      const codePoint = binaryString.substr(i, byteCount * 8);
  
      // Convert the binary code point to decimal
      const decimalCodePoint = parseInt(codePoint, 2);
  
      // Convert the decimal code point to Unicode character
      const character = String.fromCodePoint(decimalCodePoint);
  
      // Append the character to the decoded string
      decodedString += character;
  
      // Move to the next character
      i += byteCount * 8;
    }
  
    return decodedString;
}
  
// Helper function to count the leading '1' bits in a binary string
function getLeadingOnes(binaryString) {
    let count = 0;
    for (let i = 0; i < binaryString.length; i++) {
      if (binaryString[i] === '1') {
        count++;
      } else {
        break;
      }
    }
    return count;
}

while(datarequest){
  await getContractTransactions();
}
//getContractTransactions();
