import Web3 from 'web3';

const web3 = new Web3('https://sepolia.infura.io/v3/edbaf363f322439e9b71df83782130d1'); // Replace with your Infura project ID or provide your own Ethereum node URL

const contractAddress = '0x13F790e006804B3e643db9A09EFd49Cb99f1a98D'; // Replace with your smart contract address

const abi = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "bytes32",
				"name": "id",
				"type": "bytes32"
			}
		],
		"name": "ChainlinkCancelled",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "bytes32",
				"name": "id",
				"type": "bytes32"
			}
		],
		"name": "ChainlinkFulfilled",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "bytes32",
				"name": "id",
				"type": "bytes32"
			}
		],
		"name": "ChainlinkRequested",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "to",
				"type": "address"
			}
		],
		"name": "OwnershipTransferRequested",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "to",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "bytes32",
				"name": "requestId",
				"type": "bytes32"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "price",
				"type": "uint256"
			}
		],
		"name": "RequestEthereumPriceFulfilled",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "acceptOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "_requestId",
				"type": "bytes32"
			},
			{
				"internalType": "uint256",
				"name": "_payment",
				"type": "uint256"
			},
			{
				"internalType": "bytes4",
				"name": "_callbackFunctionId",
				"type": "bytes4"
			},
			{
				"internalType": "uint256",
				"name": "_expiration",
				"type": "uint256"
			}
		],
		"name": "cancelRequest",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "currentPrice",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "_requestId",
				"type": "bytes32"
			},
			{
				"internalType": "uint256",
				"name": "_price",
				"type": "uint256"
			}
		],
		"name": "fulfillEthereumPrice",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getChainlinkToken",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_oracle",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_jobId",
				"type": "string"
			}
		],
		"name": "requestEthereumPrice",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "withdrawLink",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
];

const contract = new web3.eth.Contract(abi, contractAddress);

async function getContractTransactions() {
  try {
    const events = await contract.getPastEvents('allEvents', { fromBlock: 0, toBlock: 'latest' });

    for (let i = (events.length - 1); (events.length - 2) < i ; i--) {
      const transaction = await web3.eth.getTransaction(events[i].transactionHash);
      console.log('----------------------------------');
      const inputData = transaction.data.slice(136); // Remove the function signature from the input data
      console.log('Decode :',utf8Decode(inputData).slice(236));
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

getContractTransactions();
