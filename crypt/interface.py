from hashlib import md5
from pathlib import Path

import typer
from rich import print, prompt, table

from models import Store, Account, InitialVectors

storefile = Path(__file__).parent.joinpath("store.json").resolve()
app = typer.Typer(
    name="crypt",
    short_help="password manager",
    help="A simple password manager in your terminal",
    pretty_exceptions_show_locals=False,
)


@app.command(
    "init", short_help="create store", help="intionalizes a store with master password hash"
)
def register() -> None:
    if not storefile.exists():
        print(f"[green]creating store file at [magenta][i]'{storefile}'")
        storefile.touch()

    while True:
        master_passphrase = prompt.Prompt.ask(
            ":locked_with_key: please enter a password [magenta](must be at least 5 characters)",
            password=True
        )

        if len(master_passphrase) >= 5:
            break
        print("[prompt.invalid]password too short")

    keyhash = md5(master_passphrase.encode()).hexdigest()
    print(f"password signature: [b]{keyhash}")

    store = Store(keyhash=keyhash)

    print("[yellow]updating store file")
    storefile.write_text(store.model_dump_json(indent=2))

    print(f"[green][b]Successfuly intionalized store")
