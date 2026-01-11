# Chunk: aeca0fc73bc5_38

- source: `.venv-lab/Lib/site-packages/notebook/static/1584.5e136a9d8643093bc7e9.js`
- lines: 2473-2543
- chunk: 39/45

```
his.skipGapsTo(to, offset, -1);
            to += offset;
            size += this.chunk.length - len0;
        }
        let last = this.chunk.length - 4;
        if (this.lang.streamParser.mergeTokens && size == 4 && last >= 0 &&
            this.chunk[last] == id && this.chunk[last + 2] == from)
            this.chunk[last + 2] = to;
        else
            this.chunk.push(id, from, to, size);
        return offset;
    }
    parseLine(context) {
        let { line, end } = this.nextLine(), offset = 0, { streamParser } = this.lang;
        let stream = new StringStream(line, context ? context.state.tabSize : 4, context ? getIndentUnit(context.state) : 2);
        if (stream.eol()) {
            streamParser.blankLine(this.state, stream.indentUnit);
        }
        else {
            while (!stream.eol()) {
                let token = readToken(streamParser.token, stream, this.state);
                if (token)
                    offset = this.emitToken(this.lang.tokenTable.resolve(token), this.parsedPos + stream.start, this.parsedPos + stream.pos, offset);
                if (stream.start > 10000 /* C.MaxLineLength */)
                    break;
            }
        }
        this.parsedPos = end;
        this.moveRangeIndex();
        if (this.parsedPos < this.to)
            this.parsedPos++;
    }
    finishChunk() {
        let tree = _lezer_common__WEBPACK_IMPORTED_MODULE_0__.Tree.build({
            buffer: this.chunk,
            start: this.chunkStart,
            length: this.parsedPos - this.chunkStart,
            nodeSet,
            topID: 0,
            maxBufferLength: 2048 /* C.ChunkSize */,
            reused: this.chunkReused
        });
        tree = new _lezer_common__WEBPACK_IMPORTED_MODULE_0__.Tree(tree.type, tree.children, tree.positions, tree.length, [[this.lang.stateAfter, this.lang.streamParser.copyState(this.state)]]);
        this.chunks.push(tree);
        this.chunkPos.push(this.chunkStart - this.ranges[0].from);
        this.chunk = [];
        this.chunkReused = undefined;
        this.chunkStart = this.parsedPos;
    }
    finish() {
        return new _lezer_common__WEBPACK_IMPORTED_MODULE_0__.Tree(this.lang.topNode, this.chunks, this.chunkPos, this.parsedPos - this.ranges[0].from).balance();
    }
}
function readToken(token, stream, state) {
    stream.start = stream.pos;
    for (let i = 0; i < 10; i++) {
        let result = token(stream, state);
        if (stream.pos > stream.start)
            return result;
    }
    throw new Error("Stream parser failed to advance stream.");
}
const noTokens = /*@__PURE__*/Object.create(null);
const typeArray = [_lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeType.none];
const nodeSet = /*@__PURE__*/new _lezer_common__WEBPACK_IMPORTED_MODULE_0__.NodeSet(typeArray);
const warned = [];
// Cache of node types by name and tags
const byTag = /*@__PURE__*/Object.create(null);
const defaultTable = /*@__PURE__*/Object.create(null);
for (let [legacyName, name] of [
```
