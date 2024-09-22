const net = require('net');

// Configuration
const host = '192.168.0.2';
const port = 50051;
const name = 'John';

// Create a socket instance
const client = new net.Socket();

// Connect to the server
client.connect(port, host, () => {
    console.log(`Connected to server on ${host}:${port}`);
    client.write(name);
});

client.on('data', (data) => {
    console.log(`Received: ${data.toString()}`);
    client.destroy(); // Close the connection after receiving the response
});

client.on('close', () => {
    console.log('Connection closed');
});

client.on('error', (err) => {
    console.error(`Error: ${err}`);
});
