const net = require('net');

// Configuration
const host = '192.168.0.2';
const port = 50051;

// Create a server instance
const server = net.createServer((socket) => {
    console.log(`Connected by ${socket.remoteAddress}:${socket.remotePort}`);

    socket.on('data', (data) => {
        const name = data.toString().trim();
        const response = `hello, ${name}`;
        socket.write(response);
    });

    socket.on('end', () => {
        console.log(`Connection from ${socket.remoteAddress}:${socket.remotePort} ended`);
    });

    socket.on('error', (err) => {
        console.error(`Error: ${err}`);
    });
});

// Bind the server to the specified host and port
server.listen(port, host, () => {
    console.log(`Server listening on ${host}:${port}`);
});
