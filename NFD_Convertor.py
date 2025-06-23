import os
import unicodedata
import tkinter as tk
from tkinter import messagebox, ttk

# tkinterdnd2 is required for native drag-and-drop support
# Install with: pip install tkinterdnd2
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    raise ImportError("Please install tkinterdnd2: pip install tkinterdnd2")

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
        self.convert_btn.pack(side='left', padx=(0,5))
        self.clear_btn.pack(side='left')

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

    def _preprocess_name(self, name):
        base, ext = os.path.splitext(name)
        processed = base.replace(' ', '_').lower() + ext
        return unicodedata.normalize('NFC', processed)

    def _convert_all(self):
        if not self.all_paths:
            messagebox.showwarning("No items", "Please drop items first.")
            return
        # Rename from deepest paths first
        for oldpath in sorted(self.all_paths, key=lambda p: p.count(os.sep), reverse=True):
            parent = os.path.dirname(oldpath)
            original = os.path.basename(oldpath)
            new_name = self._preprocess_name(original)
            newpath = os.path.join(parent, new_name)
            if oldpath != newpath:
                try:
                    os.rename(oldpath, newpath)
                    # update drop_roots if needed
                    if oldpath in self.drop_roots:
                        idx = self.drop_roots.index(oldpath)
                        self.drop_roots[idx] = newpath
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to convert '{oldpath}': {e}")
                    return
        messagebox.showinfo("Done", "All items have been normalized to NFC.")
        self._refresh_tree()

    def _clear_list(self, clear_roots=True):
        for iid in self.tree.get_children(''):
            self.tree.delete(iid)
        self.all_paths.clear()
        if clear_roots:
            self.drop_roots.clear()

if __name__ == '__main__':
    app = BatchConverterApp()
    app.mainloop()
