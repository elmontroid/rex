# Rex
A password manager in your terminal build using python.

## Installation
**Run *pip install rex* in the directory where you downloaded the source code**

## Usage

### Initializing store
```bash
python rex init
```

### Adding account
```bash
python rex add <site-name>
```
**Replace *site-name* with the name of the account to use, example: "github"**

### Getting account passphrase
```bash
python rex get <site-name>
```
**Replace *site-name* with the name of the account to use, example: "github"**

### Removing an account
```bash
python rex remove <site-name>
```
**Replace *site-name* with the name of the account to use, example: "github"**

### List accounts
```bash
python rex list
```
