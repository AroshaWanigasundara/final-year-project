import { exec } from 'child_process';

// Replace 'your_python_script.py' with the path to your Python script
//const pythonScriptPath = 'mytest.py';

// Replace 'parameterValue' with the value you want to pass as a parameter
const parameterValue = 'bafybeidp6tp3oeizgyoqwrzdxq5hhttumk7aeppkvsnwxrqrqinitifeju';

// Add the parameter to the command when executing the Python script
exec(`python mytest.py ${parameterValue}`, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error executing Python script: ${error.message}`);
    return;
  }

  // Process the output if needed
  console.log('Python script output:');
  console.log(stdout);
});
