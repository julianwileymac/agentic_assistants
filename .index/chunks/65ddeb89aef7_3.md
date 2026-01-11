# Chunk: 65ddeb89aef7_3

- source: `webui/.next/build/chunks/[root-of-the-server]__1359ec9e._.js`
- lines: 221-299
- chunk: 4/7

```
;
        if (recvPromiseResolve != null) {
            recvPromiseResolve(JSON.parse(packet.toString('utf8')));
        } else {
            packetQueue.push(packet);
        }
    }
    let state = {
        type: 'waiting'
    };
    let buffer = Buffer.alloc(0);
    socket.once('connect', ()=>{
        socket.setNoDelay(true);
        socket.on('data', (chunk)=>{
            buffer = Buffer.concat([
                buffer,
                chunk
            ]);
            loop: while(true){
                switch(state.type){
                    case 'waiting':
                        {
                            if (buffer.length >= 4) {
                                const length = buffer.readUInt32BE(0);
                                buffer = buffer.subarray(4);
                                state = {
                                    type: 'packet',
                                    length
                                };
                            } else {
                                break loop;
                            }
                            break;
                        }
                    case 'packet':
                        {
                            if (buffer.length >= state.length) {
                                const packet = buffer.subarray(0, state.length);
                                buffer = buffer.subarray(state.length);
                                state = {
                                    type: 'waiting'
                                };
                                pushPacket(packet);
                            } else {
                                break loop;
                            }
                            break;
                        }
                    default:
                        invariant(state, (state)=>`Unknown state type: ${state?.type}`);
                }
            }
        });
    });
    // When the socket is closed, this process is no longer needed.
    // This might happen e. g. when parent process is killed or
    // node.js pool is garbage collected.
    socket.once('close', ()=>{
        process.exit(0);
    });
    // TODO(lukesandberg): some of the messages being sent are very large and contain lots
    //  of redundant information.  Consider adding gzip compression to our stream.
    function doSend(message) {
        return new Promise((resolve, reject)=>{
            // Reserve 4 bytes for our length prefix, we will over-write after encoding.
            const packet = Buffer.from('0000' + message, 'utf8');
            packet.writeUInt32BE(packet.length - 4, 0);
            socketWritable.write(packet, (err)=>{
                process.stderr.write(`TURBOPACK_OUTPUT_D\n`);
                process.stdout.write(`TURBOPACK_OUTPUT_D\n`);
                if (err != null) {
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }
```
