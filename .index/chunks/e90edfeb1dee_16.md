# Chunk: e90edfeb1dee_16

- source: `.venv-lab/Lib/site-packages/notebook/static/6657.25b2400d23ddd24360b2.js`
- lines: 988-1059
- chunk: 17/21

```
gin ?? 50;
  _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("timeline", diagObj.db);
  const securityLevel = conf.securityLevel;
  let sandboxElement;
  if (securityLevel === "sandbox") {
    sandboxElement = (0,d3__WEBPACK_IMPORTED_MODULE_2__/* .select */ .Ys)("#i" + id);
  }
  const root = securityLevel === "sandbox" ? (0,d3__WEBPACK_IMPORTED_MODULE_2__/* .select */ .Ys)(sandboxElement.nodes()[0].contentDocument.body) : (0,d3__WEBPACK_IMPORTED_MODULE_2__/* .select */ .Ys)("body");
  const svg = root.select("#" + id);
  svg.append("g");
  const tasks2 = diagObj.db.getTasks();
  const title = diagObj.db.getCommonDb().getDiagramTitle();
  _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("task", tasks2);
  svgDraw_default.initGraphics(svg);
  const sections2 = diagObj.db.getSections();
  _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("sections", sections2);
  let maxSectionHeight = 0;
  let maxTaskHeight = 0;
  let depthY = 0;
  let sectionBeginY = 0;
  let masterX = 50 + LEFT_MARGIN;
  let masterY = 50;
  sectionBeginY = 50;
  let sectionNumber = 0;
  let hasSections = true;
  sections2.forEach(function(section) {
    const sectionNode = {
      number: sectionNumber,
      descr: section,
      section: sectionNumber,
      width: 150,
      padding: 20,
      maxHeight: maxSectionHeight
    };
    const sectionHeight = svgDraw_default.getVirtualNodeHeight(svg, sectionNode, conf);
    _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("sectionHeight before draw", sectionHeight);
    maxSectionHeight = Math.max(maxSectionHeight, sectionHeight + 20);
  });
  let maxEventCount = 0;
  let maxEventLineLength = 0;
  _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("tasks.length", tasks2.length);
  for (const [i, task] of tasks2.entries()) {
    const taskNode = {
      number: i,
      descr: task,
      section: task.section,
      width: 150,
      padding: 20,
      maxHeight: maxTaskHeight
    };
    const taskHeight = svgDraw_default.getVirtualNodeHeight(svg, taskNode, conf);
    _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("taskHeight before draw", taskHeight);
    maxTaskHeight = Math.max(maxTaskHeight, taskHeight + 20);
    maxEventCount = Math.max(maxEventCount, task.events.length);
    let maxEventLineLengthTemp = 0;
    for (const event of task.events) {
      const eventNode = {
        descr: event,
        section: task.section,
        number: task.section,
        width: 150,
        padding: 20,
        maxHeight: 50
      };
      maxEventLineLengthTemp += svgDraw_default.getVirtualNodeHeight(svg, eventNode, conf);
    }
    if (task.events.length > 0) {
      maxEventLineLengthTemp += (task.events.length - 1) * 10;
    }
    maxEventLineLength = Math.max(maxEventLineLength, maxEventLineLengthTemp);
  }
```
