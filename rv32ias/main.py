import argparse
from pathlib import Path

from rv32ias import assembler


def main():
    parser = argparse.ArgumentParser(description='RISC-V RV32I Assembler')
    parser.add_argument('asm_file', type=str, help='Assembly file to be assembled')
    args = parser.parse_args()

    asm_file = Path(args.asm_file)

    if not asm_file.exists():
        print(f'Error: {asm_file} does not exist')
        return

    with open(asm_file, 'r') as f:
        asm_txt = f.read()

    for i, machine_code in enumerate(assembler.assemble(asm_txt)):
        print(f'{i * 4:04x}: {machine_code:08x}')
