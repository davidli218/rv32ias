import argparse
from pathlib import Path
from typing import List, Dict

from rv32ias.assembler import assemble_instructions
from rv32ias.exceptions import AsmDuplicateLabelError
from rv32ias.exceptions import AsmInvalidInstructionError
from rv32ias.exceptions import AsmInvalidRegisterError
from rv32ias.exceptions import AsmInvalidSyntaxError
from rv32ias.exceptions import AsmUndefinedLabelError
from rv32ias.models import Instruction
from rv32ias.preprocessor import AsmParser


def main():
    parser = argparse.ArgumentParser(description='RISC-V RV32I Assembler')
    parser.add_argument('asm_file', type=str, help='Assembly file to be assembled')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print verbose output')
    args = parser.parse_args()

    try:
        asm = load_asm(args.asm_file)
    except FileNotFoundError as e:
        print(e)
        return

    try:
        asm_parser = AsmParser(asm)
    except (
            AsmDuplicateLabelError,
            AsmInvalidInstructionError,
            AsmInvalidRegisterError,
            AsmInvalidSyntaxError,
            AsmUndefinedLabelError
    ) as e:
        print(e)
        return

    if args.verbose:
        verbose_output(asm_parser.instructions, asm_parser.jump_table)
    else:
        standard_output(asm_parser.instructions)


def load_asm(asm_file: str) -> str:
    if not Path(asm_file).exists():
        raise FileNotFoundError(f'Error: File {asm_file} does not exist')

    with open(asm_file, 'r') as f:
        return f.read()


def standard_output(instructions: List[Instruction]) -> None:
    for machine_code in assemble_instructions(instructions):
        print(f'{machine_code:08X}')


def verbose_output(instructions: List[Instruction], targets: Dict[str, int]) -> None:
    machine_codes = assemble_instructions(instructions)

    add2label = {}
    for label, addr in targets.items():
        add2label[addr] = add2label[addr] + f', {label}' if addr in add2label else label

    max_asm_length = max(len(inst.asm) for inst in instructions)
    max_tgt_length = max([len(target) for target in add2label.values()] + [5])

    print(f"{'Addr':^9} | {'Label':^{max_tgt_length}} | {'Hex':^8} | {'Bin':^32} | {'Assembly':^{max_asm_length}}")
    print(f"{'-' * 9} | {'-' * max_tgt_length} | {'-' * 8} | {'-' * 32} | {'-' * max_asm_length}")
    for i, instruction, machine_code in zip(range(len(instructions)), instructions, machine_codes):
        print(
            f'+{i * 4:08} | {add2label.get(i * 4, ""):^{max_tgt_length}} |'
            f' {machine_code:08X} | {machine_code:032b} | {instruction.asm}'
        )


if __name__ == '__main__':
    main()
