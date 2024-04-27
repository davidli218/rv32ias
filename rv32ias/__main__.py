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
    parsed_asm = asm_parser.asm
    instructions = asm_parser.instructions
    jump_table = asm_parser.jump_table

    machine_codes = assemble_instructions(instructions)

    add2label = {}
    for label, addr in jump_table.items():
        add2label[addr] = add2label[addr] + f', {label}' if addr in add2label else label

    add2mc = {inst.idx: mc for inst, mc in zip(instructions, machine_codes)}

    max_asm_length = max(
        len(parsed_asm[inst.idx].raw) if pretty else len(parsed_asm[inst.idx].body) for inst in instructions
    )
    max_tgt_length = max([len(target) for target in add2label.values()] + [5])

    print(f"{'Addr':^9} | {'Label':^{max_tgt_length}} | {'Hex':^8} | {'Bin':^32} | {'Assembly':^{max_asm_length}}")
    print(f"{'-' * 9} | {'-' * max_tgt_length} | {'-' * 8} | {'-' * 32} | {'-' * max_asm_length}")
    for line in parsed_asm:
        if not pretty and (line.idx not in add2mc):
            continue

        if line.idx not in add2mc:
            print(f'{"*":^9} | {"":^{max_tgt_length}} | {"*":^8} | {"*":^32} | ', end='')
        else:
            machine_code = add2mc[line.idx]
            print(
                f'+{line.idx * 4:08} | {add2label.get(line.im_ptr, ""):^{max_tgt_length}} |'
                f' {machine_code:08X} | {machine_code:032b} | ', end=''
            )

        match pretty:
            case 'rainbow':
                print(line.colorize())
            case 'full':
                print(line)
            case _:
                print(line.body)


if __name__ == '__main__':
    exit(main())
