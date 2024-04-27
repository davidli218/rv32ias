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
    # Instruction memory pointer
    im_ptr: int
    # Raw line content from the original assembly code
    raw: str
    # Clean line content without comments and leading/trailing whitespaces
    body: str
    # Offset of the clean line in the raw line
    body_offset: int
    # Tailing comment
    tc: Optional[str] = None
    # Tailing comment offset
    tc_offset: Optional[int] = None

    def colorize(self):
        match self.type:
            case AsmLineType.EMPTY:
                return f'\033[41m{self.raw}\033[0m'
            case AsmLineType.COMMENT:
                a = self.raw[:self.body_offset]
                b = self.raw[self.body_offset:self.body_offset + len(self.body)]
                c = self.raw[self.body_offset + len(self.body):]
                return f'\033[45m{a}\033[47m{b}\033[41m{c}\033[0m'
            case AsmLineType.LABEL | AsmLineType.INSTRUCTION:
                color = '\033[44m' if self.type == AsmLineType.LABEL else '\033[42m'
                a = self.raw[:self.body_offset]
                b = self.raw[self.body_offset:self.body_offset + len(self.body)]
                if self.tc:
                    c = self.raw[self.body_offset + len(self.body):self.tc_offset]
                    d = self.raw[self.tc_offset:self.tc_offset + len(self.tc)]
                    e = self.raw[self.tc_offset + len(self.tc):]
                    return f'\033[45m{a}{color}{b}\033[45m{c}\033[47m{d}\033[41m{e}\033[0m'
                else:
                    c = self.raw[self.body_offset + len(self.body):]
                    return f'\033[45m{a}{color}{b}\033[41m{c}\033[0m'

    def __str__(self):
        return self.raw
