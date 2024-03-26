import re
from typing import List, Dict

from rv32ias.isa import rv32i_inst_dict
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
    asm_txt = re.sub(r'\s*\)', ')', asm_txt)

    # Format labels to end with a colon
    asm_txt = re.sub(r'^(\w+)\s*:', lambda m: m.group(1).lower() + ':', asm_txt, flags=re.MULTILINE)

    # Format instructions to 4 characters and lowercase
    asm_txt = re.sub(r'^(\w+)\s+', lambda m: m.group(1).lower().ljust(5), asm_txt, flags=re.MULTILINE)

    return asm_txt


def __parse_asm_one(single_asm: str, jump_targets: dict, pc: int) -> Instruction:
    inst, args = single_asm.split(maxsplit=1)

    if inst not in rv32i_inst_dict:
        raise ValueError(f'Instruction "{inst}" not supported')

    match = re.match(rv32i_inst_dict[inst].inst_arg_re, args)

    if not match:
        raise ValueError(f'Invalid syntax for: line {single_asm}')

    match_dict = match.groupdict()

    if 'label' in match_dict:
        label = match_dict['label']

        if label.isdigit():
            match_dict['imm'] = int(label)
        elif label in jump_targets:
            match_dict['imm'] = jump_targets[label] - pc
        else:
            raise ValueError(f'Undefined label: {label}')

        match_dict.pop('label')

    return Instruction(single_asm, inst, **match_dict)


def parse_asm(asm_pure: str) -> (List[Instruction], Dict[str, int]):
    asm_lines = asm_pure.splitlines()
    jump_targets = {}

    alc = 0
    while alc < len(asm_lines):
        line = asm_lines[alc]

        if re.match(r'^\w+:', line):
            label = line.split(':')[0]

            if label in jump_targets:
                raise ValueError(f'Duplicate label: {label}')

            jump_targets[label] = alc * 4
            asm_lines.pop(alc)
            alc -= 1

        alc += 1

    return [__parse_asm_one(line, jump_targets, i * 4) for i, line in enumerate(asm_lines)], jump_targets
