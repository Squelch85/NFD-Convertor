import os
import unicodedata
import argparse
import types
import tkinter as tk
from tkinter import messagebox, ttk


def preprocess_name(name: str) -> str:
    """Normalize and sanitize a filename."""
    base, ext = os.path.splitext(name)
    processed = base.replace(" ", "_").lower() + ext
    return unicodedata.normalize("NFC", processed)


def _gather_paths(paths):
    """Return a flattened list of all files and folders under given paths."""
    result = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                for d in dirs:
                    result.append(os.path.join(root, d))
                for f in files:
                    result.append(os.path.join(root, f))
        else:
            result.append(p)
    return result


def convert_cli(paths):
    """Convert paths in command line mode."""
    all_paths = _gather_paths(paths)
    total = len(all_paths)
    for idx, oldpath in enumerate(sorted(all_paths, key=lambda p: p.count(os.sep), reverse=True), 1):
        parent = os.path.dirname(oldpath)
        original = os.path.basename(oldpath)
        new_name = preprocess_name(original)
        newpath = os.path.join(parent, new_name)
        if oldpath != newpath:
            os.rename(oldpath, newpath)
        print(f"[{idx}/{total}] {oldpath} -> {newpath}")
    print("Done.")

# tkinterdnd2 is required for native drag-and-drop support. When it is not
# available (such as in testing environments), fall back to the standard Tk
# class so that CLI functionality still works.
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:  # pragma: no cover - optional dependency
    DND_FILES = "DND_Files"
    class _DummyTk(tk.Tk):
        pass
    TkinterDnD = types.SimpleNamespace(Tk=_DummyTk)

class BatchConverterApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Batch File Converter (NFD→NFC)")
        self.geometry("700x500")
        self.configure(bg='#2e2e2e')  # Dark background

        # Enable drag-and-drop on root
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_drop)

        # Dark mode style
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview', background='#3e3e3e', fieldbackground='#3e3e3e', foreground='#ffffff')
        style.configure('Treeview.Heading', background='#2e2e2e', foreground='#ffffff')
        style.configure('TButton', background='#4e4e4e', foreground='#ffffff')
        style.map('TButton', background=[('active', '#5e5e5e')])

        # Tracking dropped roots and all paths
        self.drop_roots = []  # original dropped files/folders
        self.all_paths = []   # flattened list of every file and folder path

        # Treeview for hierarchical display
        self.tree = ttk.Treeview(self, show='tree')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        # Enable drag-and-drop on the tree widget too
        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind('<<Drop>>', self._on_drop)

        # Control buttons
        btn_frame = tk.Frame(self, bg='#2e2e2e')
        btn_frame.pack(fill='x', padx=10, pady=(0,10))
        self.convert_btn = ttk.Button(btn_frame, text="Convert to NFC", command=self._convert_all)
        self.clear_btn = ttk.Button(btn_frame, text="Clear List", command=self._clear_list)
        self.progress = ttk.Progressbar(btn_frame, mode='determinate')
        self.convert_btn.pack(side='left', padx=(0,5))
        self.clear_btn.pack(side='left')
        self.progress.pack(fill='x', expand=True, padx=10, side='right')

    def _split_paths(self, data):
        return [p.strip() for p in self.tk.splitlist(data)]

    def _on_drop(self, event):
        paths = self._split_paths(event.data)
        for path in paths:
            if path not in self.drop_roots:
                self.drop_roots.append(path)
        self._refresh_tree()

    def _refresh_tree(self):
        self._clear_list(clear_roots=False)
        self.all_paths.clear()
        for root in self.drop_roots:
            self._add_item(root, parent='')

    def _add_item(self, path, parent):
        name = os.path.basename(path) or path
        is_dir = os.path.isdir(path)
        icon = '📁' if is_dir else '📄'
        self.tree.insert(parent, 'end', iid=path, text=f"{icon} {name}")
        self.all_paths.append(path)
        if is_dir:
            try:
                for entry in sorted(os.listdir(path)):
                    full = os.path.join(path, entry)
                    self._add_item(full, parent=path)
            except PermissionError:
                pass


    def _convert_all(self):
        if not self.all_paths:
            messagebox.showwarning("No items", "Please drop items first.")
            return
        # Rename from deepest paths first
        total = len(self.all_paths)
        self.progress.configure(maximum=total, value=0)
        for idx, oldpath in enumerate(sorted(self.all_paths, key=lambda p: p.count(os.sep), reverse=True), 1):
            parent = os.path.dirname(oldpath)
            original = os.path.basename(oldpath)
            new_name = preprocess_name(original)
            newpath = os.path.join(parent, new_name)
            if oldpath != newpath:
                try:
                    os.rename(oldpath, newpath)
                    # update drop_roots if needed
                    if oldpath in self.drop_roots:
                        ridx = self.drop_roots.index(oldpath)
                        self.drop_roots[ridx] = newpath
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to convert '{oldpath}': {e}")
                    self.progress['value'] = 0
                    return
            self.progress['value'] = idx
            self.update_idletasks()
        messagebox.showinfo("Done", "All items have been normalized to NFC.")
        self.progress['value'] = 0
        self._refresh_tree()

    def _clear_list(self, clear_roots=True):
        for iid in self.tree.get_children(''):
            self.tree.delete(iid)
        self.all_paths.clear()
        if clear_roots:
            self.drop_roots.clear()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NFD to NFC filename converter')
    parser.add_argument('paths', nargs='*', help='Files or directories to convert')
    parser.add_argument('--cli', action='store_true', help='Run in command line mode')
    args = parser.parse_args()

    if args.cli or args.paths:
        if not args.paths:
            parser.error('Please provide at least one path to convert.')
        convert_cli(args.paths)
    else:
        app = BatchConverterApp()
        app.mainloop()
