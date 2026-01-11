# Chunk: e90edfeb1dee_18

- source: `.venv-lab/Lib/site-packages/notebook/static/6657.25b2400d23ddd24360b2.js`
- lines: 1120-1181
- chunk: 19/21

```
tr("y2", depthY).attr("stroke-width", 4).attr("stroke", "black").attr("marker-end", "url(#arrowhead)");
  (0,_chunk_ABZYJK2D_mjs__WEBPACK_IMPORTED_MODULE_0__/* .setupGraphViewbox */ .j7)(
    void 0,
    svg,
    conf.timeline?.padding ?? 50,
    conf.timeline?.useMaxWidth ?? false
  );
}, "draw");
var drawTasks = /* @__PURE__ */ (0,_chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .__name */ .eW)(function(diagram2, tasks2, sectionColor, masterX, masterY, maxTaskHeight, conf, maxEventCount, maxEventLineLength, maxSectionHeight, isWithoutSections) {
  for (const task of tasks2) {
    const taskNode = {
      descr: task.task,
      section: sectionColor,
      number: sectionColor,
      width: 150,
      padding: 20,
      maxHeight: maxTaskHeight
    };
    _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("taskNode", taskNode);
    const taskWrapper = diagram2.append("g").attr("class", "taskWrapper");
    const node = svgDraw_default.drawNode(taskWrapper, taskNode, sectionColor, conf);
    const taskHeight = node.height;
    _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("taskHeight after draw", taskHeight);
    taskWrapper.attr("transform", `translate(${masterX}, ${masterY})`);
    maxTaskHeight = Math.max(maxTaskHeight, taskHeight);
    if (task.events) {
      const lineWrapper = diagram2.append("g").attr("class", "lineWrapper");
      let lineLength = maxTaskHeight;
      masterY += 100;
      lineLength = lineLength + drawEvents(diagram2, task.events, sectionColor, masterX, masterY, conf);
      masterY -= 100;
      lineWrapper.append("line").attr("x1", masterX + 190 / 2).attr("y1", masterY + maxTaskHeight).attr("x2", masterX + 190 / 2).attr("y2", masterY + maxTaskHeight + 100 + maxEventLineLength + 100).attr("stroke-width", 2).attr("stroke", "black").attr("marker-end", "url(#arrowhead)").attr("stroke-dasharray", "5,5");
    }
    masterX = masterX + 200;
    if (isWithoutSections && !conf.timeline?.disableMulticolor) {
      sectionColor++;
    }
  }
  masterY = masterY - 10;
}, "drawTasks");
var drawEvents = /* @__PURE__ */ (0,_chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .__name */ .eW)(function(diagram2, events, sectionColor, masterX, masterY, conf) {
  let maxEventHeight = 0;
  const eventBeginY = masterY;
  masterY = masterY + 100;
  for (const event of events) {
    const eventNode = {
      descr: event,
      section: sectionColor,
      number: sectionColor,
      width: 150,
      padding: 20,
      maxHeight: 50
    };
    _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("eventNode", eventNode);
    const eventWrapper = diagram2.append("g").attr("class", "eventWrapper");
    const node = svgDraw_default.drawNode(eventWrapper, eventNode, sectionColor, conf);
    const eventHeight = node.height;
    maxEventHeight = maxEventHeight + eventHeight;
    eventWrapper.attr("transform", `translate(${masterX}, ${masterY})`);
    masterY = masterY + 10 + eventHeight;
  }
```
