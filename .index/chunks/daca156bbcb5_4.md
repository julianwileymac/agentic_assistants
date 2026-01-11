# Chunk: daca156bbcb5_4

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_core_lib-0053df.js`
- lines: 194-220
- chunk: 5/5

```
                    continue;
                }
                xhr.setRequestHeader(k, options.headers[k]);
            }
        }
    }
    getResponseHeaders(xhr) {
        const headers = {};
        for (const line of xhr.getAllResponseHeaders().split(/\r\n|\n|\r/g)) {
            if (line) {
                const idx = line.indexOf(':');
                headers[line.substring(0, idx).trim().toLowerCase()] = line.substring(idx + 1).trim();
            }
        }
        return headers;
    }
};
XHRBrowserRequestService = (0, tslib_1.__decorate)([
    (0, inversify_1.injectable)()
], XHRBrowserRequestService);
exports.XHRBrowserRequestService = XHRBrowserRequestService;


/***/ }

}]);
//# sourceMappingURL=C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_core_lib-0053df.js.map
```
