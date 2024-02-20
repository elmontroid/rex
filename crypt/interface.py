from hashlib import md5
from pathlib import Path

from rich import print
from rich.prompt import Prompt, Confirm

import typer

import models


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


@app.command("init", short_help="create store", help="intionalizes a store with master password hash")
def register() -> None:
    if not storefile.exists():
        print(f"creating store file at [magenta][i]'{storefile}'")
        storefile.touch()

    elif not storefile.read_text() == "" and not Confirm.ask("[yellow]overwrite existing store"):
        error("overwrite permission denied", code=2)

    while True:
        master_passphrase = Prompt.ask(":locked_with_key: enter new master passphrase [magenta](must be at least 5 characters)", password=True)
        if len(master_passphrase) >= 5:
            break

        print("[prompt.invalid]passphrase too short")

    keyhash = md5(master_passphrase.encode()).hexdigest()
    print(f"passphrase signature: [b]{keyhash}")

    store = models.Store(keyhash=keyhash)
    store_json = store.model_dump_json(indent=2)

    storefile.write_text(store_json)
    print("[green][b]Successfuly intionalized store")
