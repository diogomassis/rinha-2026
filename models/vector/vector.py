from dataclasses import dataclass

@dataclass
class VectorLabel:
    vector: list[float]
    label: str
