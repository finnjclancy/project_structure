const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");
const fs = require("fs");

async function whichPython() {
  const candidates = ["python3", "python", "py"];
  for (const c of candidates) {
    try {
      cp.execFileSync(c, ["--version"], { stdio: "ignore" });
      return c;
    } catch {}
  }
  return null;
}

function activate(context) {
  const cmd = vscode.commands.registerCommand("projectStructure.generate", async () => {
    const ws = vscode.workspace.workspaceFolders?.[0];
    if (!ws) {
      vscode.window.showErrorMessage("open a folder first");
      return;
    }

    const py = await whichPython();
    if (!py) {
      vscode.window.showErrorMessage("python not found on path");
      return;
    }

    const cwd = ws.uri.fsPath;
    // point to the python script in the extension root
    const scriptPath = path.join(context.extensionPath, "make_structure.py");
    const outPath = path.join(cwd, "project_structure.txt");

    cp.execFile(py, [scriptPath], { cwd }, async (err, stdout, stderr) => {
      if (err) {
        vscode.window.showErrorMessage(`script failed. ${stderr || err.message}`);
        return;
      }
      if (!fs.existsSync(outPath)) {
        vscode.window.showWarningMessage("no output file found");
        return;
      }
      vscode.window.showInformationMessage("project_structure.txt updated");
      const uri = vscode.Uri.file(outPath);
      const doc = await vscode.workspace.openTextDocument(uri);
      vscode.window.showTextDocument(doc);
    });
  });

  context.subscriptions.push(cmd);
}

function deactivate() {}

module.exports = { activate, deactivate };