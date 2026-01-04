/**
 * MLFlow extension icons
 */

import { LabIcon } from '@jupyterlab/ui-components';

// MLFlow icon SVG
const mlflowSvg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
</svg>
`;

const experimentSvg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
  <path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
</svg>
`;

const runSvg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
  <path d="M5 3l14 9-14 9V3z"/>
</svg>
`;

const refreshSvg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
  <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
</svg>
`;

export const mlflowIcon = new LabIcon({
  name: 'mlflow:logo',
  svgstr: mlflowSvg
});

export const experimentIcon = new LabIcon({
  name: 'mlflow:experiment',
  svgstr: experimentSvg
});

export const runIcon = new LabIcon({
  name: 'mlflow:run',
  svgstr: runSvg
});

export const refreshIcon = new LabIcon({
  name: 'mlflow:refresh',
  svgstr: refreshSvg
});

