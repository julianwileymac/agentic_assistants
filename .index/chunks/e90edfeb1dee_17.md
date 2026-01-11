# Chunk: e90edfeb1dee_17

- source: `.venv-lab/Lib/site-packages/notebook/static/6657.25b2400d23ddd24360b2.js`
- lines: 1050-1128
- chunk: 18/21

```
ht: 50
      };
      maxEventLineLengthTemp += svgDraw_default.getVirtualNodeHeight(svg, eventNode, conf);
    }
    if (task.events.length > 0) {
      maxEventLineLengthTemp += (task.events.length - 1) * 10;
    }
    maxEventLineLength = Math.max(maxEventLineLength, maxEventLineLengthTemp);
  }
  _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("maxSectionHeight before draw", maxSectionHeight);
  _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("maxTaskHeight before draw", maxTaskHeight);
  if (sections2 && sections2.length > 0) {
    sections2.forEach((section) => {
      const tasksForSection = tasks2.filter((task) => task.section === section);
      const sectionNode = {
        number: sectionNumber,
        descr: section,
        section: sectionNumber,
        width: 200 * Math.max(tasksForSection.length, 1) - 50,
        padding: 20,
        maxHeight: maxSectionHeight
      };
      _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("sectionNode", sectionNode);
      const sectionNodeWrapper = svg.append("g");
      const node = svgDraw_default.drawNode(sectionNodeWrapper, sectionNode, sectionNumber, conf);
      _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("sectionNode output", node);
      sectionNodeWrapper.attr("transform", `translate(${masterX}, ${sectionBeginY})`);
      masterY += maxSectionHeight + 50;
      if (tasksForSection.length > 0) {
        drawTasks(
          svg,
          tasksForSection,
          sectionNumber,
          masterX,
          masterY,
          maxTaskHeight,
          conf,
          maxEventCount,
          maxEventLineLength,
          maxSectionHeight,
          false
        );
      }
      masterX += 200 * Math.max(tasksForSection.length, 1);
      masterY = sectionBeginY;
      sectionNumber++;
    });
  } else {
    hasSections = false;
    drawTasks(
      svg,
      tasks2,
      sectionNumber,
      masterX,
      masterY,
      maxTaskHeight,
      conf,
      maxEventCount,
      maxEventLineLength,
      maxSectionHeight,
      true
    );
  }
  const box = svg.node().getBBox();
  _chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .log */ .cM.debug("bounds", box);
  if (title) {
    svg.append("text").text(title).attr("x", box.width / 2 - LEFT_MARGIN).attr("font-size", "4ex").attr("font-weight", "bold").attr("y", 20);
  }
  depthY = hasSections ? maxSectionHeight + maxTaskHeight + 150 : maxTaskHeight + 100;
  const lineWrapper = svg.append("g").attr("class", "lineWrapper");
  lineWrapper.append("line").attr("x1", LEFT_MARGIN).attr("y1", depthY).attr("x2", box.width + 3 * LEFT_MARGIN).attr("y2", depthY).attr("stroke-width", 4).attr("stroke", "black").attr("marker-end", "url(#arrowhead)");
  (0,_chunk_ABZYJK2D_mjs__WEBPACK_IMPORTED_MODULE_0__/* .setupGraphViewbox */ .j7)(
    void 0,
    svg,
    conf.timeline?.padding ?? 50,
    conf.timeline?.useMaxWidth ?? false
  );
}, "draw");
```
