import { Web3Storage } from 'web3.storage'
import fs from 'fs'
import fetch from 'node-fetch'
import axios from 'axios'
import { CID } from 'multiformats';
import { createReadStream, createWriteStream } from 'fs';
import { CarReader } from '@ipld/car';
//const axios = require('axios');

function getAccessToken () {
  // If you're just testing, you can paste in a token
  // and uncomment the following line:
  return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweDRmRkNCMTBFREQyZEYyMzFFODE2YjZGNGZCMkE0MzU4NjM4OGI3ZjQiLCJpc3MiOiJ3ZWIzLXN0b3JhZ2UiLCJpYXQiOjE2ODcxOTI1Nzg1ODAsIm5hbWUiOiJGTFN5c3RlbSJ9.aSh7AiqP8V7a6qDAX7xmdlppY9QPX-12A-pTUSME3TM'

  // In a real app, it's better to read an access token from an
  // environement variable or other configuration that's kept outside of
  // your code base. For this to work, you need to set the
  // WEB3STORAGE_TOKEN environment variable before you run your code.
  //return process.env.WEB3STORAGE_TOKEN
}

function makeStorageClient () {
  return new Web3Storage({ token: getAccessToken() })
}

/*async function retrieveFiles (cid) {
    const client = makeStorageClient()
    const res = await client.get(cid)
    console.log(`Got a response! [${res.status}] ${res.statusText}`)
    if (!res.ok) {
      throw new Error(`failed to get ${cid} - [${res.status}] ${res.statusText}`)
    }
  
    // unpack File objects from the response
    const files = await res.files()
    console.log(`${files.cid} -- ${files.path} -- ${files.size}`)
    for (const file of files) {
      console.log(`${file.cid} -- ${file.path} -- ${file.size}`)
    }
}*/
  
const filePath = './my-file.txt'

async function downloadFiles (cid) {
  const client = makeStorageClient()
  const res = await client.get(cid)
  const url = res.url;
  const saveToFile = true;  // Set to false if you want to save the data in a variable instead

  /*fetch(url)
    .then(response => response.text())
    .then(data => {
      if (saveToFile) {
        fs.writeFile(filePath, data, err => {
          if (err) throw err;
          console.log('Data saved to file!');
        });
      } else {
        // Save data in a variable
        const dataVariable = data;
        console.log('Data saved in a variable!');
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });*/
  console.log(res)
  //const gatewayURL = 'https://your-ipfs-gateway.com';

  axios.get(url, { responseType: 'stream' })
  .then(response => {
    const carReader = CarReader.fromIterable(response.data);
    let rootCID;

    const getNextBlock = async (iterator) => {
      const { value, done } = await iterator.next();
      if (done) {
        return;
      }
      const block = value[1];
      if (block.cid.equals(block.root)) {
        rootCID = block.cid;
      }
      return getNextBlock(iterator);
    };

    getNextBlock(carReader.blocks())
      .then(() => {
        if (rootCID) {
          const saveDirectory = async (node, path) => {
            if (node.isDir()) {
              fs.mkdirSync(path, { recursive: true });
              for await (const entry of node.content()) {
                await saveDirectory(await entry[1].cid(), `${path}/${entry[0]}`);
              }
            } else {
              const content = await node.content();
              content.pipe(createWriteStream(path));
            }
          };

          saveDirectory(carReader.get(rootCID), 'downloaded_folder')
            .then(() => {
              console.log('Folder saved successfully.');
            })
            .catch(error => {
              console.error('Error:', error);
            });
        } else {
          console.error('Root CID not found in the CAR file.');
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
  })
  .catch(error => {
    console.error('Error:', error);
  });

}

const args = process.argv.slice(2);
//retrieveFiles(JSON.parse(args[0]));
//downloadFiles(JSON.parse(args[0]));
downloadFiles('bafybeihprs7fftjtmuyryz5gh5ofqyzodcxeu2mklqqnrbfpgllvixdvfu'); 