# Crypt
A password manager in your terminal build using python.

## Usage

### Initializing store
```bash
python crypt init
```

### Adding account
```bash
python crypt add <site-name>
```
**Replace *site-name* with the name of the account to use, example: "github"**

### Getting account passphrase
```bash
python crypt get <site-name>
```
**Replace *site-name* with the name of the account to use, example: "github"**

### Removing an account
```bash
python crypt remove <site-name>
```
**Replace *site-name* with the name of the account to use, example: "github"**

### List accounts
```bash
python crypt list
```
