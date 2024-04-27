import argparse

from rv32ias.assembler import assemble_instructions
from rv32ias.exceptions import AsmParseError
from rv32ias.preprocessor import AsmParser


def main():
    parser = argparse.ArgumentParser(description='RISC-V RV32I Assembler')
    parser.add_argument('asm_file', type=str, help='Assembly file to be assembled')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print verbose output')
    parser.add_argument('--pretty', '-p', type=str, help='Pretty print verbose output')
    parser.add_argument('--binary', '-b', action='store_true', help='Output binary instead of hex')
    parser.add_argument('--output', '-o', type=str, help='Output file to write to')

    args = parser.parse_args()

    if args.verbose and (args.binary or args.output):
        print("Error: --verbose cannot be used with --binary or --output")
        return 1

    if not args.verbose and args.pretty:
        print("Error: --pretty can only be used with --verbose")
        return 1

    if args.pretty and args.pretty not in ('rainbow', 'full'):
        print("Error: --pretty can only be 'rainbow' or 'full'")
        return 1

    try:
        raw_asm = load_asm(args.asm_file)
        asm_parser = AsmParser(raw_asm)
    except (FileNotFoundError, AsmParseError) as e:
        print(e)
        return 1

    if args.verbose:
        verbose_output(asm_parser, args.pretty)
    else:
        standard_output(asm_parser, args.binary, args.output)

    return 0


def load_asm(asm_file: str) -> str:
    try:
        with open(asm_file, 'r') as f:
            return f.read()
    except Exception as e:
        raise FileNotFoundError(f"Error occurred while reading file:\n -> {e}")


def standard_output(asm_parser: AsmParser, binary: bool, output: str) -> None:
    if output:
        with open(output, 'w') as f:
            for machine_code in assemble_instructions(asm_parser.instructions):
                f.write(f'{machine_code:08X}\n' if not binary else f'{machine_code:032b}\n')
    else:
        for machine_code in assemble_instructions(asm_parser.instructions):
            print(f'{machine_code:08X}' if not binary else f'{machine_code:032b}')


def verbose_output(asm_parser: AsmParser, pretty: str) -> None:
    asm = asm_parser.asm

    # Build a mapping from instruction index to machine code
    machine_codes = {inst.idx: mc for inst, mc in zip(
        asm_parser.instructions, assemble_instructions(asm_parser.instructions)
    )}

    # Build a mapping from instruction memory address to jump label
    jump_table = {}
    for label, addr in asm_parser.jump_table.items():
        jump_table[addr] = jump_table[addr] + f', {label}' if addr in jump_table else label

    # Calculate pretty print lengths
    max_asm_length = max(len(asm[idx].raw) if pretty else len(asm[idx].body) for idx in machine_codes)
    max_tgt_length = max([len(target) for target in jump_table.values()] + [5])

    # Print the header
    print(f"{'Addr':^9} | {'Label':^{max_tgt_length}} | {'Hex':^8} | {'Bin':^32} | {'Assembly':^{max_asm_length}}")
    print(f"{'-' * 9} | {'-' * max_tgt_length} | {'-' * 8} | {'-' * 32} | {'-' * max_asm_length}")

    for line in asm:
        if not pretty and line.idx not in machine_codes:
            continue

        if line.idx not in machine_codes:
            print(f'{"*":^9} | {"":^{max_tgt_length}} | {"*":^8} | {"*":^32} | ', end='')
        else:
            print(
                f'+{line.idx * 4:08} | {jump_table.get(line.im_ptr, ""):^{max_tgt_length}} |'
                f' {machine_codes[line.idx]:08X} | {machine_codes[line.idx]:032b} | ', end=''
            )

        print(
            line.colorize() if pretty == 'rainbow' else
            line.raw if pretty == 'full' else
            line.body
        )


if __name__ == '__main__':
    exit(main())
