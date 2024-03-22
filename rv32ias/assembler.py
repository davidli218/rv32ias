import re
from dataclasses import dataclass
from typing import List, Dict, Optional

from rv32ias.isa import InstDef
from rv32ias.isa import InstType
from rv32ias.isa import reg_mapper
from rv32ias.isa import supported_instructions

inst_dict: Dict[str, InstDef] = {inst.inst: inst for inst in supported_instructions}


@dataclass
class Instruction:
    asm: str
    inst: str
    rd: Optional[str] = None
    rs1: Optional[str] = None
    rs2: Optional[str] = None
    imm: Optional[str] = None


def preprocessor(asm_txt: str) -> str:
    # Remove comments
    asm_txt = re.sub(r'#.*', '', asm_txt)

    # Remove empty lines
    asm_txt = re.sub(r'\n+', '\n', asm_txt)

    # Remove leading and trailing whitespaces
    asm_txt = re.sub(r'^\s+|\s+$', '', asm_txt, flags=re.MULTILINE)

    return asm_txt


def __parse_asm_one(single_asm: str) -> Instruction:
    inst, args = single_asm.split(maxsplit=1)

    if inst not in inst_dict:
        raise ValueError(f'Instruction "{inst}" not supported')

    match = re.match(inst_dict[inst].inst_arg_re, args)

    if not match:
        raise ValueError(f'Invalid syntax for: line {single_asm}')

    return Instruction(single_asm, inst, **match.groupdict())


def parse_asm(asm: str) -> List[Instruction]:
    return [__parse_asm_one(line) for line in asm.splitlines()]


def __assemble_handle_type_r(instruction: Instruction) -> int:
    inst_def = inst_dict[instruction.inst]

    opcode = inst_def.opcode
    funct3 = inst_def.funct3
    funct7 = inst_def.funct7

    rd = reg_mapper(instruction.rd)
    rs1 = reg_mapper(instruction.rs1)
    rs2 = reg_mapper(instruction.rs2)

    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def __assemble_handle_type_i(instruction: Instruction) -> int:
    inst_def = inst_dict[instruction.inst]

    opcode = inst_def.opcode
    funct3 = inst_def.funct3

    rd = reg_mapper(instruction.rd)
    rs1 = reg_mapper(instruction.rs1)
    imm = int(instruction.imm) & 0xFFF

    return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def __assemble_handle_type_sb(instruction: Instruction) -> int:
    inst_def = inst_dict[instruction.inst]

    opcode = inst_def.opcode
    funct3 = inst_def.funct3

    rs1 = reg_mapper(instruction.rs1)
    rs2 = reg_mapper(instruction.rs2)
    imm = int(instruction.imm)

    if inst_def.inst_type == InstType.S_:
        imm7 = (imm & (0b1111111 << 5)) >> 5
        imm5 = (imm & (0b11111 << 0)) >> 0
    else:
        imm7 = ((imm & (0b1 << 12)) >> 6) | ((imm & (0b111111 << 5)) >> 5)
        imm5 = ((imm & (0b1111 << 1)) >> 0) | ((imm & (0b1 << 11)) >> 11)

    return (imm7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm5 << 7) | opcode


def __assemble_handle_type_uj(instruction: Instruction) -> int:
    inst_def = inst_dict[instruction.inst]

    opcode = inst_def.opcode

    rd = reg_mapper(instruction.rd)
    imm = int(instruction.imm)

    if inst_def.inst_type == InstType.J_:
        imm20 = (imm & (0b1 << 20)) >> 20
        imm10_1 = (imm & (0b1111111111 << 1)) >> 1
        imm11 = (imm & (0b1 << 11)) >> 11
        imm19_12 = (imm & (0b11111111 << 12)) >> 12
        imm = (imm20 << 19) | (imm10_1 << 9) | (imm11 << 8) | (imm19_12 << 0)
    else:
        imm = imm & 0xFFFFF000

    return (imm << 12) | (rd << 7) | opcode


def __assemble_instruction(instruction: Instruction) -> int:
    match inst_dict[instruction.inst].inst_type:
        case InstType.R_:
            return __assemble_handle_type_r(instruction)
        case InstType.I_:
            return __assemble_handle_type_i(instruction)
        case InstType.S_ | InstType.B_:
            return __assemble_handle_type_sb(instruction)
        case InstType.U_ | InstType.J_:
            return __assemble_handle_type_uj(instruction)
        case _:
            raise ValueError(f'Instruction type not supported: {inst_dict[instruction.inst].inst_type}')


def assemble_instructions(instructions: List[Instruction]) -> List[int]:
    return [__assemble_instruction(line) for line in instructions]


def assemble(asm_txt: str) -> List[int]:
    return assemble_instructions(parse_asm(preprocessor(asm_txt)))
