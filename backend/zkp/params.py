from dataclasses import dataclass


@dataclass(frozen=True)
class SchnorrParams:
    p: int
    q: int
    g: int


# Demo parameters for prototyping. For production, replace these with reviewed
# domain parameters where q divides p - 1 and g has order q in Z_p*.
DEMO_PARAMS = SchnorrParams(
    p=23,
    q=11,
    g=2,
)

