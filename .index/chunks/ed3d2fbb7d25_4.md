# Chunk: ed3d2fbb7d25_4

- source: `frontend/browser-app/lib/frontend/vendors-C_Users_Julian_Wiley_Documents_GitHub_agentic_assistants_frontend_node_modules_theia_-7f5c5b.js`
- lines: 143-219
- chunk: 5/6

```
'theia/filesystem/prepareDownload', 'Preparing download...');
            const [progress, result] = await Promise.all([
                this.messageService.showProgress({
                    text: text,
                    options: { cancelable: true }
                }, () => { cancel = true; }),
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                new Promise(async (resolve) => {
                    const resp = await fetch(this.request(uris));
                    const jsonResp = await resp.json();
                    resolve({ response: resp, jsonResponse: jsonResp });
                })
            ]);
            const { response, jsonResponse } = result;
            if (cancel) {
                this.cancelDownload(jsonResponse.id);
                return;
            }
            const { status, statusText } = response;
            if (status === 200) {
                progress.cancel();
                const downloadUrl = `${this.endpoint()}/download/?id=${jsonResponse.id}`;
                if (copyLink) {
                    if (document.documentElement) {
                        const toDispose = (0, widgets_1.addClipboardListener)(document.documentElement, 'copy', e => {
                            toDispose.dispose();
                            this.handleCopy(e, downloadUrl);
                        });
                        document.execCommand('copy');
                    }
                }
                else {
                    this.forceDownload(jsonResponse.id, decodeURIComponent(jsonResponse.name));
                }
            }
            else {
                throw new Error(`Received unexpected status code: ${status}. [${statusText}]`);
            }
        }
        catch (e) {
            this.logger.error(`Error occurred when downloading: ${uris.map(u => u.toString(true))}.`, e);
        }
    }
    async forceDownload(id, title) {
        let url;
        try {
            if (this.anchor === undefined) {
                this.anchor = document.createElement('a');
            }
            const endpoint = this.endpoint();
            url = `${endpoint}/download/?id=${id}`;
            this.anchor.href = url;
            this.anchor.style.display = 'none';
            this.anchor.download = title;
            document.body.appendChild(this.anchor);
            this.anchor.click();
        }
        finally {
            // make sure anchor is removed from parent
            if (this.anchor && this.anchor.parentNode) {
                this.anchor.parentNode.removeChild(this.anchor);
            }
            if (url) {
                URL.revokeObjectURL(url);
            }
        }
    }
    request(uris) {
        const url = this.url(uris);
        const init = this.requestInit(uris);
        return new Request(url, init);
    }
    requestInit(uris) {
        if (uris.length === 1) {
            return {
                body: undefined,
```
