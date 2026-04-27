import datetime, json, math, os, sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import dialogs
from makePublicPrivateKeys import generateKey
import publicKeyCipher


class SecretMessengerTk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.basedir = os.path.dirname(__file__)

        # ---- app state ----
        self.SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 !?'.,-:;()$/&%+_@\n\\\t"
        self.user = None
        self.privKey = None
        self.pubKey = None
        self.n = None
        self.d = None

        # ---- window ----
        self.title("Secret Messenger")
        self.geometry("1100x780")
        self.minsize(900, 650)

        # ---- user selection (Tk dialog) ----
        self.select_user_or_exit()

        # ---- address book + keys ----
        self.address_book_file = os.path.join(self.basedir, f"{self.user}s_address_book.json")
        self.ensure_address_book()
        self.load_address_book()
        self.load_or_create_keys()

        # ---- UI ----
        self.mode_var = tk.StringVar(value="encrypt")  # "encrypt" or "decrypt"
        self.status_var = tk.StringVar(value="Ready")

        self.make_widgets()
        self.refresh_mode_ui()

    # -----------------------------
    # Data / setup
    # -----------------------------
    def select_user_or_exit(self):
        dlg = dialogs.UserSelectionDialog(parent=self, basedir=self.basedir, keys_filename="keys.json")
        self.wait_window(dlg)
        if not getattr(dlg, "result_ok", False):
            raise SystemExit("User selection cancelled.")
        self.user = dlg.user

    def ensure_address_book(self):
        if not os.path.exists(self.address_book_file):
            with open(self.address_book_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def load_address_book(self):
        with open(self.address_book_file, "r", encoding="utf-8") as f:
            self.address_book = json.load(f)

    def load_or_create_keys(self):
        keys_path = os.path.join(self.basedir, "keys.json")
        key_data = {}
        if os.path.exists(keys_path):
            try:
                with open(keys_path, "r", encoding="utf-8") as f:
                    key_data = json.load(f)
            except Exception:
                key_data = {}

        if self.user in key_data:
            priv = key_data[self.user]["privKey"]
            pub = key_data[self.user]["pubKey"]
            self.n = int(priv[0])
            self.d = int(priv[1])
            self.privKey = (self.n, self.d)
            self.pubKey = (int(pub[0]), int(pub[1]))
        else:
            privKey, pubKey = generateKey(1024)
            self.n = int(privKey[0])
            self.d = int(privKey[1])
            self.privKey = (self.n, self.d)
            self.pubKey = (int(pubKey[0]), int(pubKey[1]))

            key_data[self.user] = {
                "privKey": [str(self.privKey[0]), str(self.privKey[1])],
                "pubKey": [str(self.pubKey[0]), str(self.pubKey[1])],
            }
            with open(keys_path, "w", encoding="utf-8") as f:
                json.dump(key_data, f, indent=4, sort_keys=True)

    # -----------------------------
    # UI
    # -----------------------------
    def make_widgets(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Radiobutton(
            top, text="Encrypt a message", value="encrypt",
            variable=self.mode_var, command=self.refresh_mode_ui
        ).pack(side="left", padx=(0, 10))

        ttk.Radiobutton(
            top, text="Decrypt a ciphertext", value="decrypt",
            variable=self.mode_var, command=self.refresh_mode_ui
        ).pack(side="left")

        ttk.Button(top, text="Share my public key", command=self.share_pubkey).pack(side="right", padx=(10, 0))
        ttk.Button(top, text="Change user", command=self.reset_user).pack(side="right")

        main = ttk.Frame(self, padding=(10, 0, 10, 10))
        main.pack(fill="both", expand=True)

        # Left column (input)
        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Input").pack(anchor="w")
        self.input_text = tk.Text(left, height=25, wrap="word")
        self.input_text.pack(fill="both", expand=True)

        left_controls = ttk.Frame(left)
        left_controls.pack(fill="x", pady=8)

        ttk.Label(left_controls, text="Addressee").pack(side="left")

        self.addressee_var = tk.StringVar()
        self.addressee_combo = ttk.Combobox(
            left_controls,
            textvariable=self.addressee_var,
            values=list(self.address_book.keys()),
            width=30,
            state="readonly",
        )
        self.addressee_combo.pack(side="left", padx=8)
        if self.address_book:
            self.addressee_combo.current(0)

        ttk.Button(left_controls, text="Add addressee", command=self.add_addressee).pack(side="left")
        ttk.Button(left_controls, text="Paste", command=self.paste_clipboard).pack(side="right")

        # Middle (process button)
        mid = ttk.Frame(main, padding=10)
        mid.pack(side="left", fill="y")
        self.process_btn = ttk.Button(mid, text="Encrypt", command=self.on_submit)
        self.process_btn.pack(pady=10)

        # Right column (output)
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(right, text="Output").pack(anchor="w")
        self.output_text = tk.Text(right, height=25, wrap="word")
        self.output_text.pack(fill="both", expand=True)
        self.output_text.configure(state="disabled")

        right_controls = ttk.Frame(right)
        right_controls.pack(fill="x", pady=8)

        ttk.Button(right_controls, text="Clear fields", command=self.clear_fields).pack(side="left")
        ttk.Button(right_controls, text="Copy", command=self.copy_output).pack(side="right", padx=(8, 0))
        ttk.Button(right_controls, text="Save", command=self.save_output).pack(side="right")

        status = ttk.Frame(self, padding=6)
        status.pack(fill="x", side="bottom")
        ttk.Label(status, text="Status:").pack(side="left")
        ttk.Label(status, textvariable=self.status_var).pack(side="left", padx=8)

    def refresh_mode_ui(self):
        mode = self.mode_var.get()
        if mode == "encrypt":
            self.process_btn.configure(text="Encrypt")
            self.addressee_combo.configure(state="readonly")
            self.set_input_placeholder_encrypt()
            self.set_status("Ready")
        else:
            self.process_btn.configure(text="Decrypt")
            self.addressee_combo.configure(state="disabled")
            self.set_input_placeholder_decrypt()
            self.set_status("Ready")

    def set_status(self, msg):
        self.status_var.set(msg)

    def set_output(self, text):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.configure(state="disabled")

    def get_input(self):
        return self.input_text.get("1.0", "end-1c")

    def clear_fields(self):
        self.input_text.delete("1.0", "end")
        self.set_output("")

    def copy_output(self):
        text = self.output_text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.set_status("Content copied to clipboard")

    def paste_clipboard(self):
        try:
            text = self.clipboard_get()
        except tk.TclError:
            text = ""
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", text)

    def set_input_placeholder_encrypt(self):
        if not self.get_input().strip():
            self.input_text.insert(
                "1.0",
                "Write or paste the text to encrypt.\n\n"
                "Avoid exotic symbols.\n\n"
                "Select the public key of the recipient (addressee) from the dropdown.\n"
            )

    def set_input_placeholder_decrypt(self):
        if not self.get_input().strip():
            self.input_text.insert("1.0", "Paste the ciphertext (comma-separated integers) here.")

    # -----------------------------
    # Actions
    # -----------------------------
    def add_addressee(self):
        dlg = dialogs.addAddresseeDialog(
            parent=self,
            address_book=self.address_book,
            address_book_filename=self.address_book_file,
            basedir=self.basedir,
        )
        self.wait_window(dlg)

        if not getattr(dlg, "result_ok", False):
            self.set_status("Addressee dialog cancelled")
            return

        # dialog already persisted to JSON, but we also refresh in-memory + combobox
        self.load_address_book()
        self.addressee_combo.configure(values=list(self.address_book.keys()))
        self.addressee_var.set(dlg.new_addressee)
        self.set_status(f"Addressee {dlg.new_addressee} was added successfully")

    def share_pubkey(self):
        dlg = dialogs.showPubKeyDialog(parent=self, user=self.user, public_key=self.pubKey, basedir=self.basedir)
        self.wait_window(dlg)

    def reset_user(self):
        self.destroy()
        app = SecretMessengerTk()
        app.mainloop()

    def save_output(self):
        file = filedialog.asksaveasfilename(
            title="Save",
            filetypes=[("Text files", "*.txt")],
            defaultextension=".txt",
        )
        if not file:
            return

        current_daytime = datetime.datetime.now()
        formatted_datetime = current_daytime.strftime('_%Y%m%d_%H%M')

        if self.mode_var.get() == "encrypt":
            addressee = self.addressee_var.get()
            header = f"This message was encrypted for {addressee} on {formatted_datetime}.\n\n"
        else:
            header = f"This is a decrypted message for {self.user}'s eyes only.\n\n"

        content = header + self.output_text.get("1.0", "end-1c")
        try:
            with open(file, "w", encoding="utf-8") as f:
                f.write(content)
            self.set_status(f"Content successfully exported with path: {file}")
        except Exception as e:
            self.set_status(f"Save failed: {e}")

    def on_submit(self):
        text = self.get_input()

        if self.mode_var.get() == "encrypt":
            if not self.address_book:
                messagebox.showerror("No addressees", "Your address book is empty.")
                return
            addressee = self.addressee_var.get()
            if not addressee:
                messagebox.showerror("No addressee", "Select an addressee.")
                return

            try:
                n_str, e_str = self.address_book[addressee]
                n, e = int(n_str), int(e_str)
            except Exception:
                messagebox.showerror("Bad key", "Selected addressee has an invalid public key.")
                return

            blockSize = 160

            self.set_status("Encrypting...")
            try:
                encrypted_blocks = publicKeyCipher.encryptMessage(text, (n, e), blockSize)
                encrypted_content = ",".join(str(b) for b in encrypted_blocks)
                self.set_output(encrypted_content)
                self.set_status("Encryption successful!")
            except Exception as ex:
                messagebox.showerror("Encryption error", str(ex))
                self.set_status("Encryption failed")

        else:
            self.set_status("Decrypting...")
            encryptedMessage = text.strip()
            if not encryptedMessage:
                return

            blockSize = 160

            try:
                encryptedBlocks = [int(b) for b in encryptedMessage.split(",") if b.strip() != ""]
            except ValueError:
                messagebox.showerror("Invalid ciphertext", "Ciphertext must be comma-separated integers.")
                self.set_status("Decrypt failed")
                return

            ciphertext_length_guess = blockSize * len(encryptedBlocks)

            try:
                secret_message = publicKeyCipher.decryptMessage(
                    encryptedBlocks,
                    ciphertext_length_guess,
                    (int(self.n), int(self.d)),
                    blockSize
                )
                self.set_output(secret_message)
                self.set_status("Secret message successfully decrypted!")
            except Exception as ex:
                messagebox.showerror("Decryption error", str(ex))
                self.set_status("Decrypt failed")


if __name__ == "__main__":
    app = SecretMessengerTk()
    app.mainloop()