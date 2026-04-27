import ast
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# -----------------------------
# small helpers
# -----------------------------
def _ensure_json_file(path: str, default_obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_obj, f)


def _load_json(path: str, default_obj):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_obj


def _save_json(path: str, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, sort_keys=True)


def _center_over_parent(win: tk.Toplevel, parent: tk.Misc | None):
    win.update_idletasks()
    if parent is None:
        return
    try:
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
    except Exception:
        return
    w = win.winfo_width()
    h = win.winfo_height()
    x = px + (pw // 2) - (w // 2)
    y = py + (ph // 2) - (h // 2)
    win.geometry(f"+{x}+{y}")


# -----------------------------
# dialogs
# -----------------------------
class UserSelectionDialog(tk.Toplevel):
    """
    Tkinter replacement for your PyQt UserSelectionDialog.

    - Displays currently available users (from keys.json).
    - Allows selecting an existing user OR registering a new user in the same dialog.

    After closing:
      - result_ok: True if OK pressed with valid data, else False
      - user: selected/created username
      - address_book: "<user>s_address_book.json"
    """

    def __init__(self, parent=None, basedir=None, keys_filename="keys.json"):
        super().__init__(parent)

        self.parent = parent
        self.basedir = basedir or os.path.dirname(__file__)
        self.keys_path = os.path.join(self.basedir, keys_filename)

        _ensure_json_file(self.keys_path, {})

        self.user = ""
        self.address_book = ""
        self.result_ok = False

        self.title("Select username")
        self.resizable(False, False)
        self.geometry("420x360")

        # Load existing users
        self._key_data = _load_json(self.keys_path, {})
        self._users = sorted(list(self._key_data.keys()))

        container = ttk.Frame(self, padding=14)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Available users:", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")

        # Show available users clearly (listbox)
        list_frame = ttk.Frame(container)
        list_frame.pack(fill="x", pady=(6, 10))

        self.users_listbox = tk.Listbox(list_frame, height=7, exportselection=False)
        yscroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.users_listbox.yview)
        self.users_listbox.configure(yscrollcommand=yscroll.set)

        self.users_listbox.pack(side="left", fill="x", expand=True)
        yscroll.pack(side="right", fill="y")

        for u in self._users:
            self.users_listbox.insert("end", u)

        if self._users:
            self.users_listbox.selection_set(0)

        ttk.Separator(container).pack(fill="x", pady=10)

        ttk.Label(container, text="Or register a new user:", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")

        new_user_row = ttk.Frame(container)
        new_user_row.pack(fill="x", pady=(6, 0))

        self.create_var = tk.BooleanVar(value=False)
        self.create_check = ttk.Checkbutton(
            new_user_row,
            text="Create new user",
            variable=self.create_var,
            command=self._toggle_new_user,
        )
        self.create_check.pack(side="left")

        self.new_user_var = tk.StringVar()
        self.new_user_entry = ttk.Entry(container, textvariable=self.new_user_var)
        self.new_user_entry.pack(fill="x", pady=(6, 0))
        self.new_user_entry.configure(state="disabled")

        hint = (
            "Tip: To create a new user, check 'Create new user' and enter a name.\n"
            "Otherwise, select an existing user from the list."
        )
        ttk.Label(container, text=hint, foreground="#555").pack(anchor="w", pady=(10, 0))

        btns = ttk.Frame(container)
        btns.pack(fill="x", pady=(14, 0))

        ttk.Button(btns, text="Cancel", command=self._cancel).pack(side="left")
        ttk.Button(btns, text="OK", command=self._ok).pack(side="right")

        # convenience bindings
        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self._cancel())

        # modal-ish behavior
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        _center_over_parent(self, parent)

    def _toggle_new_user(self):
        if self.create_var.get():
            self.new_user_entry.configure(state="normal")
            self.new_user_entry.focus_set()
        else:
            self.new_user_entry.configure(state="disabled")

    def _cancel(self):
        self.result_ok = False
        self.destroy()

    def _ok(self):
        if self.create_var.get():
            user = self.new_user_var.get().strip()
            if not user:
                messagebox.showerror("Invalid username", "Please enter a username.", parent=self)
                return
            self.user = user
        else:
            if not self._users:
                messagebox.showerror(
                    "No users available",
                    "No existing users found.\n\nCheck 'Create new user' to register one.",
                    parent=self,
                )
                return

            sel = self.users_listbox.curselection()
            if not sel:
                messagebox.showerror("No selection", "Please select a user from the list.", parent=self)
                return
            self.user = self.users_listbox.get(sel[0]).strip()

        self.address_book = f"{self.user}s_address_book.json"
        self.result_ok = True
        self.destroy()


class showPubKeyDialog(tk.Toplevel):
    """
    Tkinter replacement for your PyQt showPubKeyDialog.

    Expects public_key in the same shape you used in your JSON: ["n", "e"] (strings)
    but will also accept (n, e) ints.
    """

    def __init__(self, parent=None, user="", public_key=None, basedir=None):
        super().__init__(parent)

        self.parent = parent
        self.basedir = basedir or os.path.dirname(__file__)
        self.user = user

        self.title("Share your public key")
        self.geometry("520x420")
        self.minsize(520, 420)

        if public_key is None:
            public_key = ["", ""]

        n, e = public_key
        keystring = f"['{n}', '{e}']"

        container = ttk.Frame(self, padding=14)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Your public key is:", font=("TkDefaultFont", 12, "bold")).pack(anchor="w")

        self.content = tk.Text(container, wrap="word", height=12)
        yscroll = ttk.Scrollbar(container, orient="vertical", command=self.content.yview)
        self.content.configure(yscrollcommand=yscroll.set)

        self.content.pack(side="left", fill="both", expand=True, pady=(8, 12))
        yscroll.pack(side="right", fill="y", pady=(8, 12))

        self.content.insert("1.0", keystring)
        self.content.configure(state="disabled")

        btns = ttk.Frame(container)
        btns.pack(fill="x")

        ttk.Button(btns, text="Copy", command=self.copy).pack(side="left")
        ttk.Button(btns, text="Save", command=self.write).pack(side="left", padx=8)
        ttk.Button(btns, text="Done", command=self.destroy).pack(side="right")

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        _center_over_parent(self, parent)

    def _get_text(self):
        return self.content.get("1.0", "end-1c")

    def copy(self):
        self.clipboard_clear()
        self.clipboard_append(self._get_text())

    def write(self):
        file = filedialog.asksaveasfilename(
            parent=self,
            title="Save public key",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )
        if not file:
            return

        content = (
            "This public key is a list or array containing two large integers stored as strings.\n\n"
            f"Here is {self.user}'s public key:\n\n"
            f"{self._get_text()}\n"
        )
        try:
            with open(file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror("Save failed", str(e), parent=self)


class addAddresseeDialog(tk.Toplevel):
    """
    Big single-dialog Add Addressee window.

    - Name entry + big key paste area in one dialog (no follow-up prompts).
    - Validates that pubkey is a list of two strings: ['n', 'e']
    - Writes back to the address book JSON.

    After closing:
      - result_ok: True if add succeeded
      - new_addressee: name if succeeded else ""
    """

    def __init__(self, parent=None, address_book=None, address_book_filename="", basedir=None):
        super().__init__(parent)

        self.parent = parent
        self.basedir = basedir or os.path.dirname(__file__)
        self.address_book = address_book if address_book is not None else {}
        self.address_book_filename = address_book_filename

        self.new_addressee = ""
        self.result_ok = False

        self.title("Add an addressee")
        self.geometry("860x650")
        self.minsize(780, 580)

        container = ttk.Frame(self, padding=14)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Add an addressee", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")

        ttk.Label(
            container,
            text="Enter a name and paste the recipient's public key (list of two strings).",
            foreground="#555",
        ).pack(anchor="w", pady=(6, 12))

        # --- name row ---
        name_row = ttk.Frame(container)
        name_row.pack(fill="x", pady=(0, 10))

        ttk.Label(name_row, text="Name:", width=10).pack(side="left", anchor="w")
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(name_row, textvariable=self.name_var)
        self.name_entry.pack(side="left", fill="x", expand=True)
        self.name_entry.focus_set()

        # --- key label ---
        ttk.Label(
            container,
            text="Public key (paste as Python list):  Example: ['123456789...', '65537']",
        ).pack(anchor="w")

        # --- big text area + scrollbar ---
        key_frame = ttk.Frame(container)
        key_frame.pack(fill="both", expand=True, pady=(6, 12))

        self.input_field = tk.Text(key_frame, wrap="word")
        yscroll = ttk.Scrollbar(key_frame, orient="vertical", command=self.input_field.yview)
        self.input_field.configure(yscrollcommand=yscroll.set)

        self.input_field.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        self.input_field.insert(
            "1.0",
            "Paste the addressee's public key here.\n\n"
            "Format must be exactly:\n"
            "['<n>', '<e>']\n"
        )

        # --- buttons ---
        btns = ttk.Frame(container)
        btns.pack(fill="x")

        ttk.Button(btns, text="Cancel", command=self._cancel).pack(side="left")
        ttk.Button(btns, text="Paste", command=self.paste).pack(side="left", padx=8)
        ttk.Button(btns, text="Add", command=self.addAddressee).pack(side="right")

        # key bindings
        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Control-v>", lambda e: (self.paste(), "break"))

        # modal-ish behavior
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        _center_over_parent(self, parent)

    def _cancel(self):
        self.result_ok = False
        self.destroy()

    def paste(self):
        try:
            text = self.clipboard_get()
        except tk.TclError:
            text = ""
        self.input_field.delete("1.0", "end")
        self.input_field.insert("1.0", text)

    def addAddressee(self):
        new_addressee_name = self.name_var.get().strip()
        if not new_addressee_name:
            messagebox.showerror("Invalid name", "Please enter a name.", parent=self)
            return

        if new_addressee_name in self.address_book:
            messagebox.showerror("Already exists", "This addressee already exists.", parent=self)
            return

        raw = self.input_field.get("1.0", "end-1c").strip()

        try:
            new_addressee_pubkey = ast.literal_eval(raw)
        except Exception:
            messagebox.showerror(
                "Invalid public key",
                "The public key is invalid.\n\nIt must look like:\n['<n>', '<e>']",
                parent=self,
            )
            return

        if (
            not isinstance(new_addressee_pubkey, list)
            or len(new_addressee_pubkey) != 2
            or not isinstance(new_addressee_pubkey[0], str)
            or not isinstance(new_addressee_pubkey[1], str)
        ):
            messagebox.showerror(
                "Invalid public key",
                "The public key must be a list of exactly two strings:\n['<n>', '<e>']",
                parent=self,
            )
            return

        # Save it
        self.address_book[new_addressee_name] = new_addressee_pubkey
        self.new_addressee = new_addressee_name

        try:
            _save_json(self.address_book_filename, self.address_book)
        except Exception as e:
            messagebox.showerror("Write failed", str(e), parent=self)
            return

        self.result_ok = True
        self.destroy()