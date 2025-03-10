import axios from 'axios'
import fs from 'fs'

function convertToList(input) {
    try {
      // Check if the input is not undefined or null
      if (input !== undefined && input !== null) {
        const parsedList = JSON.parse(input);
  
        // Check if the parsed value is an array
        if (Array.isArray(parsedList)) {
          return parsedList;
        } else {
          // If the parsed value is not an array, return an empty array
          return [];
        }
      } else {
        // If the input is undefined or null, return an empty array
        return [];
      }
    } catch (error) {
      // If an error occurs during parsing or the input is not a valid JSON string, return an empty array
      return [];
    }
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

async function getMedian(cid) {
    try {
      const weightList = [];
      const medianWeightList = [];
  
      for (let i = 1; i <= 3; i++) {
        const fileUrl = `https://${cid}.ipfs.w3s.link/weights/clients_${i}.txt`;
        const response = await axios.get(fileUrl);
        const content = response.data;
        weightList.push(content);
        // tf.keras.backend.clear_session(); // There's no direct equivalent for this line in JavaScript
      }
      /*const arrays = [
        [1, 5, -19, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 65, 69, 73, 77],
        [2, 16, -10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62, 66, 70, 74, 78],
        [3, -7, -11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63, 67, 71, 75, 79]]*/

      const resultsarray = calculateMedian(weightList);
      //const parsedWeightList = convertToList(weightList); // Use JSON.parse in JavaScript
  
      /*for (let i = 0; i < weightList[0].length; i++) {
        const gradListTuple = weightList.map(item => item[i]);
        const layerMedian = gradListTuple.reduce((acc, curr) => acc.map((val, index) => val + curr[index]), new Array(gradListTuple[0].length).fill(0));
        medianWeightList.push(layerMedian.map(val => val * gradListTuple.length));
      }*/
  
      const fileContent = JSON.stringify(resultsarray);
      const filePath = './iterations.txt';
      fs.writeFileSync(filePath, fileContent);
      console.log('successful');
    } catch (error) {
      console.error('Error:', error.message);
    }
}
getMedian("bafybeidp6tp3oeizgyoqwrzdxq5hhttumk7aeppkvsnwxrqrqinitifeju")