from typing import List

from rv32ias.assembler import assemble_instructions
from rv32ias.preprocessor import AsmParser


def assemble(asm_txt: str) -> List[int]:
    return assemble_instructions(AsmParser(asm_txt).instructions)
