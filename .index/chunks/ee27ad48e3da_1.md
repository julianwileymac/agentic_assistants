# Chunk: ee27ad48e3da_1

- source: `.venv-lab/Lib/site-packages/notebook/static/4645.86baf1dd4035fc7a4cf3.js`
- lines: 47-98
- chunk: 2/2

```
;
                if (!match) {
                    return;
                }
                const path = decodeURIComponent(match);
                commands.execute('console:create', { path });
            },
        });
        router.register({ command, pattern: consolePattern });
    },
};
/**
 * Open consoles in a new tab.
 */
const redirect = {
    id: '@jupyter-notebook/console-extension:redirect',
    requires: [_jupyterlab_console__WEBPACK_IMPORTED_MODULE_1__.IConsoleTracker],
    optional: [_jupyter_notebook_application__WEBPACK_IMPORTED_MODULE_3__.INotebookPathOpener],
    autoStart: true,
    description: 'Open consoles in a new tab',
    activate: (app, tracker, notebookPathOpener) => {
        const baseUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__.PageConfig.getBaseUrl();
        const opener = notebookPathOpener !== null && notebookPathOpener !== void 0 ? notebookPathOpener : _jupyter_notebook_application__WEBPACK_IMPORTED_MODULE_3__.defaultNotebookPathOpener;
        tracker.widgetAdded.connect(async (send, console) => {
            const { sessionContext } = console;
            await sessionContext.ready;
            const widget = (0,_lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__.find)(app.shell.widgets('main'), (w) => w.id === console.id);
            if (widget) {
                // bail if the console is already added to the main area
                return;
            }
            opener.open({
                prefix: _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__.URLExt.join(baseUrl, 'consoles'),
                path: sessionContext.path,
                target: '_blank',
            });
            // the widget is not needed anymore
            console.dispose();
        });
    },
};
/**
 * Export the plugins as default.
 */
const plugins = [opener, redirect];
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugins);


/***/ })

}]);
//# sourceMappingURL=4645.86baf1dd4035fc7a4cf3.js.map?v=86baf1dd4035fc7a4cf3
```
