# Secret Messenger (RSA Exercise)

A small educational desktop app that demonstrates **public-key cryptography (RSA)** by letting you:

- generate/load RSA keys for multiple local “users”
- store public keys for contacts (“addressees”) in an address book
- **encrypt** a message using an addressee’s **public key**
- **decrypt** a ciphertext using your **private key**

This project is intentionally simple and designed for learning, not production security.

## What this is (and what it isn’t)

### This *is*

- A basic RSA practice project.
- A way to see how RSA can encrypt data in **blocks**, turning text into integers and back again.
- A demonstration of public-key vs private-key roles.

### This is *not*

- A secure messaging application.
- A modern cryptography implementation (it does not use padding schemes like OAEP).
- A replacement for well-tested crypto libraries.

## Requirements

- Python 3.x
- Tkinter (usually included with standard Python installers on Windows/macOS)

No third-party GUI framework is required (no PyQt).

## Run

From the project folder:

```bash
python main_tk.py
```

## Files created locally (not meant to be committed)

The app stores per-user data locally:

- `keys.json` — locally generated keys (private + public)
- `*address_book.json` — saved addressees and their public keys

These should be excluded from Git. Add this to your `.gitignore`:

```gitignore
keys.json
*address_book.json
```

If you already committed them once:

```bash
git rm --cached keys.json
git rm --cached *address_book.json
git commit -m "Stop tracking local user data files"
```

## How encryption output is formatted

In the current basic version, ciphertext is shown as:

- a comma-separated list of large integers (RSA-encrypted blocks)

Example:

```
1234567890123,9876543210987, ...
```

(Optionally, a more robust format is to include message length and block size, e.g. `messageLength_blockSize_blocks...`.)

## Project structure (typical)

- `main_tk.py` — Tkinter UI entry point
- `dialogs.py` — Tkinter dialogs (user selection, add addressee, show public key)
- `makePublicPrivateKeys.py` — RSA key generation utilities
- `publicKeyCipher.py` — text↔blocks conversion and RSA encrypt/decrypt operations

## Classroom notes / suggested exercises

- Change the symbol set and observe how it affects block sizing.
- Add metadata to ciphertext (message length + block size) to improve decryption correctness.
- Explore what happens when block values become larger than `n` (and why that breaks RSA).
- Discuss why real RSA uses padding (OAEP) and why “textbook RSA” is insecure.

## License

Educational use.
