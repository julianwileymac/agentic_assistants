# Chunk: d6ceb1f4dde1_21

- source: `.venv-lab/Lib/site-packages/notebook/static/6657.25b2400d23ddd24360b2.js.map`
- lines: 1-1
- chunk: 22/22

```
[\"cScale\" + i]};\n    }\n    .edge-depth-${i - 1}{\n      stroke-width: ${sw};\n    }\n    .section-${i - 1} line {\n      stroke: ${options[\"cScaleInv\" + i]} ;\n      stroke-width: 3;\n    }\n\n    .lineWrapper line{\n      stroke: ${options[\"cScaleLabel\" + i]} ;\n    }\n\n    .disabled, .disabled circle, .disabled text {\n      fill: lightgray;\n    }\n    .disabled text {\n      fill: #efefef;\n    }\n    `;\n  }\n  return sections2;\n}, \"genSections\");\nvar getStyles = /* @__PURE__ */ __name((options) => `\n  .edge {\n    stroke-width: 3;\n  }\n  ${genSections(options)}\n  .section-root rect, .section-root path, .section-root circle  {\n    fill: ${options.git0};\n  }\n  .section-root text {\n    fill: ${options.gitBranchLabel0};\n  }\n  .icon-container {\n    height:100%;\n    display: flex;\n    justify-content: center;\n    align-items: center;\n  }\n  .edge {\n    fill: none;\n  }\n  .eventWrapper  {\n   filter: brightness(120%);\n  }\n`, \"getStyles\");\nvar styles_default = getStyles;\n\n// src/diagrams/timeline/timeline-definition.ts\nvar diagram = {\n  db: timelineDb_exports,\n  renderer: timelineRenderer_default,\n  parser: timeline_default,\n  styles: styles_default\n};\nexport {\n  diagram\n};\n"],"names":[],"sourceRoot":""}
```
