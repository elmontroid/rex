from pydantic import BaseModel, Field


class InitialVectors(BaseModel):
    username: str
    passphrase: str


class Account(BaseModel):
    salt: str
    initial_vectors: InitialVectors

    username: str
    passphrase: str


class Store(BaseModel):
    keyhash: str
    accounts: dict[str, Account] = Field(default_factory=dict)
