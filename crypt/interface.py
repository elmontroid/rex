from hashlib import md5
from pathlib import Path
from typing import Annotated, TYPE_CHECKING

import pyperclip
from rich import print
from rich.prompt import Prompt, Confirm

import typer

import cryptography
import models

if TYPE_CHECKING:
    from . import cryptography


storefile = Path(__file__).parent.joinpath("store.json").resolve()
app = typer.Typer(
    name="crypt",
    short_help="password manager",
    help="A simple password manager in your terminal",
    pretty_exceptions_show_locals=False,
)


def error(message: str, code: int = 1) -> None:
    print(f"[red][b]error:[reset] {message}")
    raise typer.Exit(code=code)


@app.command("init", short_help="Initiate store.", help="Initiate a store in the application directory with the hashed form of the master passphrase.")
def register() -> None:
    if not storefile.exists():
        print(f"creating store file at [magenta][i]'{storefile}'")
        storefile.touch()

    if not storefile.read_text() == "" and not Confirm.ask("[yellow]overwrite existing store"):
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

    storefile.write_text(store_json)
    print("[green][b]successfully initialized store")


@app.command("add", short_help="Add an account.", help="Add an account to the store encrypted using the AES encryption method.")
def add(
    site: Annotated[str, typer.Argument(show_default=False, dir_okay=False, file_okay=False)],
    overwritable: Annotated[bool, typer.Option("--overwrite", "-o", show_default=False, is_flag=True)] = False,
) -> None:
    if not storefile.exists():
        error("the store file has not been initialized, use the [i]'init'[/] command to initialize the store", code=4)

    store = models.Store.model_validate_json(storefile.read_text())

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

    storefile.write_text(store_json)
    print(f"[green][b]registered [i]{site}[/] account")

@app.command("get", short_help="Get passphrase.", help="Display or copy the passphrase of any account in the store.")
def get(
    site: Annotated[str, typer.Argument(show_default=False, dir_okay=False, file_okay=False)],
    copy: Annotated[bool, typer.Option("--copy", "-c", show_default=False, is_flag=True)] = False,
) -> None:
    if not storefile.exists():
        error("the store file has not been initialized, use the [i]'init'[/] command to initialize the store", code=4)

    store = models.Store.model_validate_json(storefile.read_text())

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

@app.command("remove", short_help="Remove an account.", help="Remove an account from store.")
def remove(
    site: Annotated[str, typer.Argument(show_default=False, dir_okay=False, file_okay=False)],
    confirmation: Annotated[bool, typer.Option("--no-input", "-ni", show_default=False, is_flag=True)] = True,
) -> None:
    if not storefile.exists():
        error("the store file has not been initialized, use the [i]'init'[/] command to initialize the store", code=4)

    store = models.Store.model_validate_json(storefile.read_text())

    if not store.accounts.__contains__(site):
        error("The account does not exist. To add a new account, use the [i]'add'[/] command.", code=2)

    if confirmation and not Confirm.ask("[yellow]remove account from store"):
        error("permission denied", code=3)

    store.accounts.pop(site)
    store_json = store.model_dump_json(indent=3)

    storefile.write_text(store_json)
    print(f"[green][b]account [i]{site}[/] removed")

@app.command("list", short_help="List accounts.", help="list every accounts from store")
def show():
    if not storefile.exists():
        error("the store file has not been initialized, use the [i]'init'[/] command to initialize the store", code=4)

    store = models.Store.model_validate_json(storefile.read_text())

    for account in store.accounts:
        print(f"[yellow][b]{account}")
