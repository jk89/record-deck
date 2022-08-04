const dgram = require('dgram');
const client = dgram.createSocket('udp4');
//client.send('Hello World!',0, 12, 12000, '127.0.0.1');

let a = require('serialport');
// console.log(a); process.exit();

let { SerialPort, ReadlineParser } = require('serialport');

async function getTeensy() {
    // const ports = await SerialPort.list();
    // const teensyPort = ports.find((port)=>port.path=="/dev/ttyACM0");
    // return teensyPort;
    return new SerialPort(
        {
            path: "/dev/ttyACM0",
            baudRate: 5000000,
            // parser: new ReadlineParser()
        }
    );
}


let i = 0;
// 3984 2048 10s 40khz
async function main() {
    const teensySerialPort = await getTeensy();
    

    // setTimeout(()=>teensySerialPort.write("somejunktoget itstarted"), 3000);

    const parser = teensySerialPort.pipe(new ReadlineParser({ delimiter: '\n' }));
    parser.on("data", (line) => {
        
        const line_split = line.split("\t");
        const network_obj = {"time": parseInt(line_split[0]), "deviceId": 0, line:line};
        const network_str = JSON.stringify(network_obj);
        // console.log(network_str);
        client.send(network_str, 8132, '192.168.0.26');
    });

    teensySerialPort.write("somejunktoget itstarted");

    // console.log("spooling up");
    /*teensySerialPort.on("data", (data) => {
        // console.log(i, );
        const line = data.toString();
        const line_split = line.split("\t");
        const network_obj = {"time": line_split[0], "deviceId": 0, line:line};
        console.log(i, line.length);
        // 
        i++;
    });*/

    return teensySerialPort;
}

main().then(console.log).catch(console.error);
