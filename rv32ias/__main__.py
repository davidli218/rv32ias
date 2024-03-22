import argparse
from pathlib import Path
from typing import List

from rv32ias.assembler import Instruction
from rv32ias.assembler import assemble_instructions
from rv32ias.assembler import clean_asm_code
from rv32ias.assembler import parse_asm


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

    instructions = parse_asm(asm)

    if args.verbose:
        verbose_output(instructions)
    else:
        standard_output(instructions)


def load_asm(asm_file: str) -> str:
    if not Path(asm_file).exists():
        raise FileNotFoundError(f'Error: File {asm_file} does not exist')

    with open(asm_file, 'r') as f:
        return clean_asm_code(f.read())


def standard_output(instructions: List[Instruction]) -> None:
    for machine_code in assemble_instructions(instructions):
        print(f'{machine_code:08X}')


def verbose_output(instructions: List[Instruction]) -> None:
    machine_codes = assemble_instructions(instructions)

    max_asm_length = max(len(inst.asm) for inst in instructions)

    print(f"{'Addr':^9} | {'Hex':^8} | {'Bin':^32} | {'Assembly':^{max_asm_length}}")
    print(f"{'-' * 9} | {'-' * 8} | {'-' * 32} | {'-' * max_asm_length}")
    for i, instruction, machine_code in zip(range(len(instructions)), instructions, machine_codes):
        print(f'+{i * 4:08X} | {machine_code:08X} | {machine_code:032b} | {instruction.asm}')


if __name__ == '__main__':
    main()
