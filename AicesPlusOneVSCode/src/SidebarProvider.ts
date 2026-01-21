import * as vscode from "vscode";
import axios from "axios";

export class SidebarProvider implements vscode.WebviewViewProvider {
    _view?: vscode.WebviewView;
    _doc?: vscode.TextDocument;

    // Default to localhost:8001
    private apiUrl = "http://localhost:8001/api/context/identify";

    constructor(private readonly _extensionUri: vscode.Uri) { }

    public resolveWebviewView(webviewView: vscode.WebviewView) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri],
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview, "<h1>No Context (Open a file)</h1>");

        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case "refresh": {
                    if (vscode.window.activeTextEditor) {
                        this.updateContext(vscode.window.activeTextEditor.document.fileName);
                    }
                    break;
                }
            }
        });
    }

    public refresh() {
        if (this._view && vscode.window.activeTextEditor) {
            this.updateContext(vscode.window.activeTextEditor.document.fileName);
        }
    }

    public async updateContext(filePath: string) {
        if (!this._view) {
            return;
        }

        this._view.webview.html = this._getHtmlForWebview(this._view.webview, "<h1>Loading...</h1>");

        try {
            const response = await axios.post(this.apiUrl, { file_path: filePath });
            const data = response.data;

            if (data.found) {
                // Encode PlantUML script for image URL
                const plantumlEncoder = require('plantuml-encoder');
                const encoded = plantumlEncoder.encode(data.uml);
                const imgUrl = `http://www.plantuml.com/plantuml/svg/${encoded}`;

                const htmlContent = `
                <div style="padding: 10px;">
                    <h3>${data.view_type.toUpperCase()} Context</h3>
                    <p><strong>Element:</strong> ${data.element.Name}</p>
                    <p><em>${data.element.Description}</em></p>
                    <hr/>
                    <div style="background: white; padding: 10px; border-radius: 4px;">
                        <img src="${imgUrl}" style="max-width: 100%;" />
                    </div>
                </div>
            `;
                this._view.webview.html = this._getHtmlForWebview(this._view.webview, htmlContent);
            } else {
                this._view.webview.html = this._getHtmlForWebview(this._view.webview, "<p>No specific architectural context found for this file.</p>");
            }

        } catch (error) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview, `<p style="color:red">Error contacting Agent API: ${error}</p>`);
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview, content: string) {
        return `<!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Architecture Context</title>
        <style>
            body { font-family: var(--vscode-font-family); color: var(--vscode-editor-foreground); padding: 0; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/plantuml-encoder@1.4.0/dist/plantuml-encoder.min.js"></script>
      </head>
      <body>
        ${content}
      </body>
      </html>`;
    }
}
