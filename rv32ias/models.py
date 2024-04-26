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
    clean: str
    # Offset of the clean line in the raw line
    clean_offset: int
    # Tailing comment
    tc: Optional[str] = None
    # Tailing comment offset
    tc_offset: Optional[int] = None

    def colorize(self):
        match self.type:
            case AsmLineType.EMPTY:
                return f'\033[41m{self.raw}\033[0m'
            case AsmLineType.COMMENT:
                a = self.raw[:self.clean_offset]
                b = self.raw[self.clean_offset:self.clean_offset + len(self.clean)]
                c = self.raw[self.clean_offset + len(self.clean):]
                return f'\033[45m{a}\033[47m{b}\033[41m{c}\033[0m'
            case AsmLineType.LABEL | AsmLineType.INSTRUCTION:
                a = self.raw[:self.clean_offset]
                b = self.raw[self.clean_offset:self.clean_offset + len(self.clean)]
                if self.tc:
                    c = self.raw[self.clean_offset + len(self.clean):self.tc_offset]
                    d = self.raw[self.tc_offset:self.tc_offset + len(self.tc)]
                    e = self.raw[self.tc_offset + len(self.tc):]
                    return f'\033[45m{a}\033[44m{b}\033[45m{c}\033[47m{d}\033[41m{e}\033[0m'
                else:
                    c = self.raw[self.clean_offset + len(self.clean):]
                    return f'\033[45m{a}\033[44m{b}\033[41m{c}\033[0m'

    def __str__(self):
        return self.raw
