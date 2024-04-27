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
        z, red, green, yellow, blue, magenta, cyan, white = (
            '\033[0m', '\033[41m', '\033[42m', '\033[43m', '\033[44m', '\033[45m', '\033[46m', '\033[47m'
        )

        if self.type == AsmLineType.EMPTY:
            return f'{red}{self.raw}{z}'

        p1 = self.raw[:self.body_offset]
        p2 = self.raw[self.body_offset:self.body_offset + len(self.body)]

        main_color = (
            magenta if self.type == AsmLineType.LABEL else
            green if self.type == AsmLineType.INSTRUCTION else
            cyan
        )

        if not self.tc:
            p3 = self.raw[self.body_offset + len(self.body):]
            return f'{white}{p1}{main_color}{p2}{red}{p3}{z}'
        else:
            p3 = self.raw[self.body_offset + len(self.body):self.tc_offset]
            p4 = self.raw[self.tc_offset:self.tc_offset + len(self.tc)]
            p5 = self.raw[self.tc_offset + len(self.tc):]
            return f'{white}{p1}{main_color}{p2}{white}{p3}{cyan}{p4}{red}{p5}{z}'

    def __str__(self):
        return self.raw
