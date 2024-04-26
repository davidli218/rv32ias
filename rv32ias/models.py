from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class Instruction:
    idx: int
    inst: str
    rd: Optional[str] = None
    rs1: Optional[str] = None
    rs2: Optional[str] = None
    imm: Optional[int] = None


class AsmLineType(Enum):
    EMPTY = 'EMPTY'
    COMMENT = 'COMMENT'
    LABEL = 'LABEL'
    INSTRUCTION = 'INSTRUCTION'


@dataclass
class AsmLine:
    # Line number in the original assembly code
    idx: int
    # Type of the line
    type: AsmLineType
    # Raw line content from the original assembly code
    raw: str
    # Clean line content without comments and leading/trailing whitespaces
    clean: str
    # Offset of the clean line in the raw line
    clean_offset: int
    # Instruction memory pointer
    im_ptr: int

    def colorize(self):
        a = self.raw[:self.clean_offset]
        b = self.raw[self.clean_offset:self.clean_offset + len(self.clean)]
        c = self.raw[self.clean_offset + len(self.clean):]

        match self.type:
            case AsmLineType.EMPTY | AsmLineType.COMMENT:
                return self.raw
            case AsmLineType.LABEL:
                return f'{a}\033[44m{b}\033[0m{c}'
            case AsmLineType.INSTRUCTION:
                return f'{a}\033[42m{b}\033[0m{c}'

    def __str__(self):
        return self.raw
