# Chunk: feff6ec6d74f_49

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 2088-2161
- chunk: 50/78

```
 `;name=${encodeURIComponent(name)};base64`);
}
function processFile(file) {
    const { name, size, type } = file;
    return new Promise((resolve, reject) => {
        const reader = new window.FileReader();
        reader.onerror = reject;
        reader.onload = (event) => {
            var _a;
            if (typeof ((_a = event.target) === null || _a === void 0 ? void 0 : _a.result) === 'string') {
                resolve({
                    dataURL: addNameToDataURL(event.target.result, name),
                    name,
                    size,
                    type,
                });
            }
            else {
                resolve({
                    dataURL: null,
                    name,
                    size,
                    type,
                });
            }
        };
        reader.readAsDataURL(file);
    });
}
function processFiles(files) {
    return Promise.all(Array.from(files).map(processFile));
}
function FileInfoPreview({ fileInfo, registry, }) {
    const { translateString } = registry;
    const { dataURL, type, name } = fileInfo;
    if (!dataURL) {
        return null;
    }
    if (type.indexOf('image') !== -1) {
        return (0,jsx_runtime.jsx)("img", { src: dataURL, style: { maxWidth: '100%' }, className: 'file-preview' });
    }
    return ((0,jsx_runtime.jsxs)(jsx_runtime.Fragment, { children: [' ', (0,jsx_runtime.jsx)("a", { download: `preview-${name}`, href: dataURL, className: 'file-download', children: translateString(lib_index_js_.TranslatableString.PreviewLabel) })] }));
}
function FilesInfo({ filesInfo, registry, preview, }) {
    if (filesInfo.length === 0) {
        return null;
    }
    const { translateString } = registry;
    return ((0,jsx_runtime.jsx)("ul", { className: 'file-info', children: filesInfo.map((fileInfo, key) => {
            const { name, size, type } = fileInfo;
            return ((0,jsx_runtime.jsxs)("li", { children: [(0,jsx_runtime.jsx)(index_modern, { children: translateString(lib_index_js_.TranslatableString.FilesInfo, [name, type, String(size)]) }), preview && (0,jsx_runtime.jsx)(FileInfoPreview, { fileInfo: fileInfo, registry: registry })] }, key));
        }) }));
}
function extractFileInfo(dataURLs) {
    return dataURLs
        .filter((dataURL) => dataURL)
        .map((dataURL) => {
        const { blob, name } = (0,lib_index_js_.dataURItoBlob)(dataURL);
        return {
            dataURL,
            name: name,
            size: blob.size,
            type: blob.type,
        };
    });
}
/**
 *  The `FileWidget` is a widget for rendering file upload fields.
 *  It is typically used with a string property with data-url format.
 */
function FileWidget(props) {
    const { disabled, readonly, required, multiple, onChange, value, options, registry } = props;
    const BaseInputTemplate = (0,lib_index_js_.getTemplate)('BaseInputTemplate', registry, options);
```
