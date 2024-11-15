from dataclasses import dataclass, field
from typing import List

@dataclass
class ImageResult:
    name: str
    prevalue: str

@dataclass
class IdentifyRes:
    imgs: List[ImageResult]  = field(default_factory=list) 
