from hashlib import md5
from pathlib import Path
from typing import Annotated

import pyperclip
from rich import print
from rich.prompt import Prompt, Confirm

import typer

from . import cryptography
from . import models

store_file = Path("~", "password-store.json").expanduser()
app = typer.Typer(name="rex", short_help="A password manager", help="A powerful password manager using AES and python", pretty_exceptions_show_locals=False)


def error(message: str, code: int = 1) -> None:
    print(f"[red][b]error:[reset] {message}")
    raise typer.Exit(code=code)


@app.command("init", help="initializes a store in home directory")
def register() -> None:
    if not store_file.exists():
        print(f"creating store file at [magenta][i]'{store_file}'")
        store_file.touch()

    if not store_file.read_text() == "" and not Confirm.ask("[yellow]overwrite existing store"):
        error("overwrite permission denied", code=3)

    while True:
        master_passphrase = Prompt.ask(":locked_with_key: enter new master passphrase [magenta](must be at least 5 characters)", password=True)
        if len(master_passphrase) >= 5:
            break

        print("[prompt.invalid]passphrase too short")

    keyhash = cryptography.hash(master_passphrase)
    print(f"passphrase signature: [b]{md5(keyhash.encode()).hexdigest()}")

    store = models.Store(keyhash=keyhash)
    store_json = store.model_dump_json(indent=3)

    store_file.write_text(store_json)
    print("[green][b]successfully initialized store")


@app.command("add", help="Adds a new password to the password manager")
def add(
    site: Annotated[str, typer.Argument(show_default=False, dir_okay=False, file_okay=False)],
    overwritable: Annotated[bool, typer.Option("--overwrite", "-o", show_default=False, is_flag=True)] = False,
) -> None:
    if not store_file.exists():
        error("the store file has not been initialized, use the [i]'init'[/] command to initialize the store", code=4)

    store = models.Store.model_validate_json(store_file.read_text())

    if store.accounts.__contains__(site) and not overwritable:
        error("the account already exists within the store, use the [i]'--overwrite'[/] flag to overwrite the existing account", code=2)

    if overwritable and store.accounts.__contains__(site) and not Confirm.ask("[yellow]overwrite existing account"):
        error("overwrite permission denied", code=3)

    master_passphrase = Prompt.ask(":locked_with_key: enter master passphrase", password=True)
    if not cryptography.verify_hash(store.keyhash, master_passphrase):
        error("incorrect master passphrase", code=5)

    passphrase = Prompt.ask(":pencil: enter account passphrase [magenta](should be at least 5 characters)", password=True)

    print(f"passphrase signature: [b]{md5(passphrase.encode()).hexdigest()}")
    
    salt = cryptography.generate_salt()
    passphrase_iv = cryptography.generate_iv()
    passphrase = cryptography.encrypt(passphrase, master_passphrase, salt, passphrase_iv)

    account = models.Account(passphrase=passphrase, salt=salt, initial_vector=passphrase_iv)

    store.accounts[site] = account

    store_json = store.model_dump_json(indent=3)

    store_file.write_text(store_json)
    print(f"[green][b]registered [i]{site}[/] account")

@app.command("get", help="Retrieves an existing password from the password manager")
def get(
    site: Annotated[str, typer.Argument(show_default=False, dir_okay=False, file_okay=False)],
    copy: Annotated[bool, typer.Option("--copy", "-c", show_default=False, is_flag=True)] = False,
) -> None:
    if not store_file.exists():
        error("the store file has not been initialized, use the [i]'init'[/] command to initialize the store", code=4)

    store = models.Store.model_validate_json(store_file.read_text())

    if not store.accounts.__contains__(site):
        error("The account does not exist. To add a new account, use the [i]'add'[/] command.", code=2)

    master_passphrase = Prompt.ask(":locked_with_key: enter master passphrase", password=True)
    if not cryptography.verify_hash(store.keyhash, master_passphrase):
        error("incorrect master passphrase", code=5)

    account = store.accounts[site]
    passphrase = cryptography.decrypt(account.passphrase, master_passphrase, account.salt, account.initial_vector)

    if not copy:
        print(f"[black]passphrase: [yellow][b]{passphrase}")
    else:
        pyperclip.copy(passphrase)
        print("[green][b]passphrase copied to clipboard")

@app.command("remove", help="Removes an existing password from the password manager")
def remove(
    site: Annotated[str, typer.Argument(show_default=False, dir_okay=False, file_okay=False)],
    confirmation: Annotated[bool, typer.Option("--no-input", "-ni", show_default=False, is_flag=True)] = True,
) -> None:
    if not store_file.exists():
        error("the store file has not been initialized, use the [i]'init'[/] command to initialize the store", code=4)

    store = models.Store.model_validate_json(store_file.read_text())

    if not store.accounts.__contains__(site):
        error("The account does not exist. To add a new account, use the [i]'add'[/] command.", code=2)

    if confirmation and not Confirm.ask("[yellow]remove account from store"):
        error("permission denied", code=3)

    store.accounts.pop(site)
    store_json = store.model_dump_json(indent=3)

    store_file.write_text(store_json)
    print(f"[green][b]account [i]{site}[/] removed")

@app.command("list", help="List all passwords in the password manager")
def show():
    if not store_file.exists():
        error("the store file has not been initialized, use the [i]'init'[/] command to initialize the store", code=4)

    store = models.Store.model_validate_json(store_file.read_text())
    accounts = [x for x in store.accounts]
    accounts.sort()

    for account in accounts:
        print(f"[yellow][b]{account}")
