# Rex
> A powerful password manager using AES and python.

## Description

Rex is a password manager that is both powerful and easy to use.
It is implemented in Python and uses advanced encryption standards (AES) to encrypt your passphrase.
All the passphrases are stored in a JSON file in your home directory.

## Installation
> Installing Rex requires python-3 or above.

To install Rex through pip run this on windows:
```powershell
pip install rex-password-manager
```

or if your using Linux operating system run this:
```bash
pip3 install rex-password-manager
```

## Usage

### Initialize a new database in Rex
This command creates a JSON file in your home directory to store all your passphrases.
It will prompt you to enter a master passphrase, which will be hashed and stored in the JSON file.
```powershell
rex init
```

### Add new passphrase using Rex
This command creates an account with the name provided as the first argument to the command.
This command will also prompts for the master passphrase and the account passphrase.
The account passphrase is encrypted using advanced encryption standards (AES) and then stored in the JSON file located in your home directory.
```powershell
rex add <name>
```

To overwrite an existing account with the same name, use the `--overwrite` flag while using this command.
```powershell
rex add --overwrite <name>
```

### Retrieve a passphrases using Rex
This command retrieves the passphrase attached to the name provided as the first argument to the command.
```powershell
rex get <name>
```

By default, this command prints out the account passphrases but you can use the `--copy` flag to copy the passphrase to your clipboard.
```powershell
rex get --copy <name>
```

### Remove a passphrase from database using Rex
This command removes an existing account with the name provided as the first argument to the command.
```powershell
rex remove <name>
```

### List account names using Rex
This command prints all the existing account names in the JSON file.
```powershell
rex list
```

