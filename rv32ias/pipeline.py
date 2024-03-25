from typing import List

from rv32ias.assembler import assemble_instructions
from rv32ias.preprocessor import clean_asm_code
from rv32ias.preprocessor import parse_asm


def assemble(asm_txt: str) -> List[int]:
    return assemble_instructions(parse_asm(clean_asm_code(asm_txt)))
