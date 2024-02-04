from typing import Any, Callable, Union, overload, NamedTuple

import nbtlib


PrimitiveNBT = Union[
    dict[str, "PrimitiveNBT"],
    list["PrimitiveNBT"],
    tuple["PrimitiveNBT", ...],
    int,
    float,
    str
]

# Doing overloads here because it's easy and static type checkers leave me alone then
@overload
def nbt_to_primitive(nbt: nbtlib.Compound) -> dict[str, PrimitiveNBT]: ...

@overload
def nbt_to_primitive(nbt: nbtlib.Base) -> PrimitiveNBT: ...

def nbt_to_primitive(nbt: nbtlib.Base) -> PrimitiveNBT:
    # NBT types inherit from their primitives (but pydantic doesn't like them)
    if isinstance(nbt, dict):
        return {key: nbt_to_primitive(value) for key, value in nbt.items()}
    if isinstance(nbt, list):
        return [nbt_to_primitive(subnbt) for subnbt in nbt]
    if isinstance(nbt, int):
        return int(nbt)
    if isinstance(nbt, float):
        return float(nbt)
    if isinstance(nbt, str):
        return str(nbt)
    if isinstance(nbt, nbtlib.Array):
        return tuple(nbt_to_primitive(subnbt) for subnbt in nbt)
    raise RuntimeError("Encountered unfamiliar nbt type!")


class Assignment[T](NamedTuple):
    path: str
    converter: Callable[[Any], T]|None = None
    nbt_converter: Callable[[nbtlib.Base], Any] = nbt_to_primitive
    optional: bool = False
    default: T|None = None
    default_factory: Callable[[], T]|None = None
    
    def __call__(self, nbt: nbtlib.Compound) -> PrimitiveNBT|None|Any:
        try:
            nbt_target = nbt[nbtlib.Path(self.path)]
        except KeyError as e:
            if self.optional:
                if self.default_factory is not None:
                    return self.default_factory()
                else:
                    return self.default
            else:
                raise
        primitive = self.nbt_converter(nbt_target)
        if self.converter is not None:
            primitive = self.converter(primitive)
        return primitive


def Submodel(subtype: "type[ConvertsNBT]", path: str="{}"):
    return Assignment(path, nbt_converter=subtype.from_nbt)

def SubmodelList[T: "ConvertsNBT"](
    path: str,
    subtype: type[T],
    optional: bool=False
) -> Assignment[list[T]]:
    return Assignment(
        path,
        nbt_converter=lambda nbt: [
            subtype.from_nbt(subnbt)
            for subnbt in nbt
        ],
        optional=optional,
        default_factory=None if not optional else lambda: []
    )


class ConvertsNBT:
    __ASSIGNMENT_TABLE__: dict[str, Assignment]
    
    @classmethod
    def from_nbt(cls, nbt: nbtlib.Compound):
        data = {}
        for attribute, assignment in cls.__ASSIGNMENT_TABLE__.items():
            data[attribute] = assignment(nbt)
        return cls(**data)