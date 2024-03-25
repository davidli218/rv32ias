import re
from typing import List

from rv32ias.isa import supported_inst_dict
from rv32ias.models import Instruction

__all__ = [
    'clean_asm_code',
    'parse_asm'
]


def clean_asm_code(asm_txt: str) -> str:
    # Remove comments
    asm_txt = re.sub(r'#.*', '', asm_txt)

    # Remove empty lines
    asm_txt = re.sub(r'\n+', '\n', asm_txt)

    # Remove leading and trailing whitespaces
    asm_txt = re.sub(r'^\s*|\s*$', '', asm_txt, flags=re.MULTILINE)

    # Remove whitespaces around commas
    asm_txt = re.sub(r'\s*,\s*', ', ', asm_txt)

    # Remove whitespaces around parentheses
    asm_txt = re.sub(r'\s*\(\s*', '(', asm_txt)
    asm_txt = re.sub(r'\s*\)\s*', ')', asm_txt)

    # Format instructions to 4 characters and lowercase
    asm_txt = re.sub(r'^(\w+)\s*', lambda m: m.group(1).lower().ljust(5), asm_txt, flags=re.MULTILINE)

    return asm_txt


def __parse_asm_one(single_asm: str) -> Instruction:
    inst, args = single_asm.split(maxsplit=1)

    if inst not in supported_inst_dict:
        raise ValueError(f'Instruction "{inst}" not supported')

    match = re.match(supported_inst_dict[inst].inst_arg_re, args)

    if not match:
        raise ValueError(f'Invalid syntax for: line {single_asm}')

    return Instruction(single_asm, inst, **match.groupdict())


def parse_asm(asm: str) -> List[Instruction]:
    return [__parse_asm_one(line) for line in asm.splitlines()]
