import * as vscode from 'vscode';
import { SidebarProvider } from './SidebarProvider';

export function activate(context: vscode.ExtensionContext) {
    const sidebarProvider = new SidebarProvider(context.extensionUri);

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            "aices-sidebar",
            sidebarProvider
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('aices.refresh', () => {
            sidebarProvider.refresh();
        })
    );

    // Listen for active text editor changes
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor) {
                sidebarProvider.updateContext(editor.document.fileName);
            }
        })
    );

    // Initial check
    if (vscode.window.activeTextEditor) {
        sidebarProvider.updateContext(vscode.window.activeTextEditor.document.fileName);
    }
}

export function deactivate() { }
