import argparse

from rv32ias.assembler import assemble_instructions
from rv32ias.exceptions import AsmParseError
from rv32ias.preprocessor import AsmParser


def main():
    parser = argparse.ArgumentParser(description='RISC-V RV32I Assembler')
    parser.add_argument('asm_file', type=str, help='Assembly file to be assembled')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print verbose output')
    args = parser.parse_args()

    try:
        raw_asm = load_asm(args.asm_file)
        asm_parser = AsmParser(raw_asm)
    except (FileNotFoundError, AsmParseError) as e:
        print(e)
        return 1

    if args.verbose:
        verbose_output(asm_parser)
    else:
        standard_output(asm_parser)

    return 0


def load_asm(asm_file: str) -> str:
    try:
        with open(asm_file, 'r') as f:
            return f.read()
    except Exception as e:
        raise FileNotFoundError(f"Error occurred while reading file:\n -> {e}")


def standard_output(asm_parser: AsmParser) -> None:
    for machine_code in assemble_instructions(asm_parser.instructions):
        print(f'{machine_code:08X}')


def verbose_output(asm_parser: AsmParser) -> None:
    parsed_asm = asm_parser.asm
    instructions = asm_parser.instructions
    jump_table = asm_parser.jump_table

    machine_codes = assemble_instructions(instructions)

    add2label = {}
    for label, addr in jump_table.items():
        add2label[addr] = add2label[addr] + f', {label}' if addr in add2label else label

    max_asm_length = max(len(parsed_asm[inst.idx].body) for inst in instructions)
    max_tgt_length = max([len(target) for target in add2label.values()] + [5])

    print(f"{'Addr':^9} | {'Label':^{max_tgt_length}} | {'Hex':^8} | {'Bin':^32} | {'Assembly':^{max_asm_length}}")
    print(f"{'-' * 9} | {'-' * max_tgt_length} | {'-' * 8} | {'-' * 32} | {'-' * max_asm_length}")
    for i, instruction, machine_code in zip(range(len(instructions)), instructions, machine_codes):
        print(
            f'+{i * 4:08} | {add2label.get(i * 4, ""):^{max_tgt_length}} |'
            f' {machine_code:08X} | {machine_code:032b} | {parsed_asm[instruction.idx].body}'
        )


if __name__ == '__main__':
    exit(main())
