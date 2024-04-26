from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class Instruction:
    line_num: int
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
    type: AsmLineType
    raw: str
    clean: str
    clean_offset: int
    im_ptr: Optional[int] = None

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
