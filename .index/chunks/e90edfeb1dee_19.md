# Chunk: e90edfeb1dee_19

- source: `.venv-lab/Lib/site-packages/notebook/static/6657.25b2400d23ddd24360b2.js`
- lines: 1174-1279
- chunk: 20/21

```
r");
    const node = svgDraw_default.drawNode(eventWrapper, eventNode, sectionColor, conf);
    const eventHeight = node.height;
    maxEventHeight = maxEventHeight + eventHeight;
    eventWrapper.attr("transform", `translate(${masterX}, ${masterY})`);
    masterY = masterY + 10 + eventHeight;
  }
  masterY = eventBeginY;
  return maxEventHeight;
}, "drawEvents");
var timelineRenderer_default = {
  setConf: /* @__PURE__ */ (0,_chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .__name */ .eW)(() => {
  }, "setConf"),
  draw
};

// src/diagrams/timeline/styles.js

var genSections = /* @__PURE__ */ (0,_chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .__name */ .eW)((options) => {
  let sections2 = "";
  for (let i = 0; i < options.THEME_COLOR_LIMIT; i++) {
    options["lineColor" + i] = options["lineColor" + i] || options["cScaleInv" + i];
    if ((0,khroma__WEBPACK_IMPORTED_MODULE_3__/* ["default"] */ .Z)(options["lineColor" + i])) {
      options["lineColor" + i] = (0,khroma__WEBPACK_IMPORTED_MODULE_4__/* ["default"] */ .Z)(options["lineColor" + i], 20);
    } else {
      options["lineColor" + i] = (0,khroma__WEBPACK_IMPORTED_MODULE_5__/* ["default"] */ .Z)(options["lineColor" + i], 20);
    }
  }
  for (let i = 0; i < options.THEME_COLOR_LIMIT; i++) {
    const sw = "" + (17 - 3 * i);
    sections2 += `
    .section-${i - 1} rect, .section-${i - 1} path, .section-${i - 1} circle, .section-${i - 1} path  {
      fill: ${options["cScale" + i]};
    }
    .section-${i - 1} text {
     fill: ${options["cScaleLabel" + i]};
    }
    .node-icon-${i - 1} {
      font-size: 40px;
      color: ${options["cScaleLabel" + i]};
    }
    .section-edge-${i - 1}{
      stroke: ${options["cScale" + i]};
    }
    .edge-depth-${i - 1}{
      stroke-width: ${sw};
    }
    .section-${i - 1} line {
      stroke: ${options["cScaleInv" + i]} ;
      stroke-width: 3;
    }

    .lineWrapper line{
      stroke: ${options["cScaleLabel" + i]} ;
    }

    .disabled, .disabled circle, .disabled text {
      fill: lightgray;
    }
    .disabled text {
      fill: #efefef;
    }
    `;
  }
  return sections2;
}, "genSections");
var getStyles = /* @__PURE__ */ (0,_chunk_AGHRB4JF_mjs__WEBPACK_IMPORTED_MODULE_1__/* .__name */ .eW)((options) => `
  .edge {
    stroke-width: 3;
  }
  ${genSections(options)}
  .section-root rect, .section-root path, .section-root circle  {
    fill: ${options.git0};
  }
  .section-root text {
    fill: ${options.gitBranchLabel0};
  }
  .icon-container {
    height:100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .edge {
    fill: none;
  }
  .eventWrapper  {
   filter: brightness(120%);
  }
`, "getStyles");
var styles_default = getStyles;

// src/diagrams/timeline/timeline-definition.ts
var diagram = {
  db: timelineDb_exports,
  renderer: timelineRenderer_default,
  parser: timeline_default,
  styles: styles_default
};



/***/ })

}]);
```
