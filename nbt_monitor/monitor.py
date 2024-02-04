from typing import Generator, Iterable, Literal
from itertools import chain
from collections import deque

import nbtlib

from nbtlib.literal.parser import Token, Parser
from rcon_monitor import RconPlayerMonitor, Client
from nbt_monitor.models import NBTInfo


class _EmptyStringNoPreambleError(ValueError):
    # This needs to be seperate from ValueError due to InvalidLiteral also being a ValueError
    ...


def _tokenize_with_preamble(raw: str) -> tuple[str, Iterable[Token]]:
    generator = nbtlib.tokenize(raw)
    
    for token in generator:
        if token.type == "COMPOUND":
            return raw[:token.span[0]], chain((token,), generator)
    raise _EmptyStringNoPreambleError("Cannot tokenize empty string")

def _iterate_until_close_compound(iterable: Iterable[Token]) -> Generator[Token, None, int]:
    # Yields from a token stream until CLOSE_COMPOUND is encountered.
    # Still yields CLOSE_COMPOUND token but also returns the ending position of the token
    # or None if the iterable was empty.
    depth = 0
    for token in iterable:
        yield token
        if token.type == "COMPOUND":
            depth += 1
        elif token.type == "CLOSE_COMPOUND":
            depth -= 1
        if depth == 0:
            return token.span[1]
    raise RuntimeError("Encountered empty tokenizer")

def tokenize_command_output(raw: str) -> Generator[
    tuple[str, deque[Token]],
    Literal[True]|None,
    None
    ]:
    """
    Tokenizes a string containing multiple NBT compounds, each with preamble.
    This is a generator function yielding a tuple of the preamble and
    the token stream for the current compound.
    
    Preamble is defined as any string that comes before a compound.
    Every compound is expected to have preamble, but not required to.
    If no preamble exists it will be an empty string.
    """
    skip_next = False
    while True:
        if skip_next:
            continue
        try:
            preamble, tokenized = _tokenize_with_preamble(raw)
        except _EmptyStringNoPreambleError:
            return
        compound_sequence = deque()
        guarded_tokenizer = _iterate_until_close_compound(tokenized)
        
        while True:
            try:
                value = next(guarded_tokenizer)
            except StopIteration as e:
                raw = raw[e.value:]
                break
            compound_sequence.append(value)
        skip_next = yield preamble, compound_sequence


class NBTMonitor(RconPlayerMonitor[str, NBTInfo]):
    def execute(self, client: Client):
        return (
            client.run("execute as @a run data get entity @s"),
        )
    
    
    def parse(self, raw: tuple[str], time: float) -> dict[str, NBTInfo]:
        data = {}
        # This will look needlessly confusing, but: 
        # There is no seperator between command outputs in RCON.
        # There is in-game, but RCON doesn't even have a space there.
        for preamble, tokens in tokenize_command_output(raw[0]):
            player_end = preamble.find(" ")
            if player_end == -1:
                print("WARNING Received invalid data in", repr(self))
                continue
            player = preamble[:player_end]
            
            nbt: nbtlib.Compound = Parser(tokens).parse()
            data[player] = NBTInfo.from_nbt(time, nbt)
        return data