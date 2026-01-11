# Chunk: adc74ce7c71e_1

- source: `frontend/browser-app/lib/frontend/C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_core_lib-3bd0ea.js`
- lines: 30-45
- chunk: 2/2

```
ider.js");
const browser_keyboard_frontend_contribution_1 = __webpack_require__(/*! ./browser-keyboard-frontend-contribution */ "C:\\Users\\Julian Wiley\\Documents\\GitHub\\agentic_assistants\\frontend\\node_modules\\@theia\\core\\lib\\browser\\keyboard\\browser-keyboard-frontend-contribution.js");
exports["default"] = new inversify_1.ContainerModule((bind, unbind, isBound, rebind) => {
    bind(browser_keyboard_layout_provider_1.BrowserKeyboardLayoutProvider).toSelf().inSingletonScope();
    bind(keyboard_layout_provider_1.KeyboardLayoutProvider).toService(browser_keyboard_layout_provider_1.BrowserKeyboardLayoutProvider);
    bind(keyboard_layout_provider_1.KeyboardLayoutChangeNotifier).toService(browser_keyboard_layout_provider_1.BrowserKeyboardLayoutProvider);
    bind(keyboard_layout_provider_1.KeyValidator).toService(browser_keyboard_layout_provider_1.BrowserKeyboardLayoutProvider);
    bind(browser_keyboard_frontend_contribution_1.BrowserKeyboardFrontendContribution).toSelf().inSingletonScope();
    bind(command_1.CommandContribution).toService(browser_keyboard_frontend_contribution_1.BrowserKeyboardFrontendContribution);
});


/***/ }

}]);
//# sourceMappingURL=C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_core_lib-3bd0ea.js.map
```
