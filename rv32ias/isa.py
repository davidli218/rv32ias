from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

__all__ = [
    'InstType',
    'supported_inst_dict',
    'reg_mapper',
]


class InstType(Enum):
    R_ = 'R'
    I_ = 'I'
    S_ = 'S'
    B_ = 'B'
    U_ = 'U'
    J_ = 'J'


@dataclass
class InstDef:
    inst: str
    inst_type: InstType
    opcode: int
    funct3: Optional[int]
    funct7: Optional[int]
    inst_arg_re: str


__inst_arg_structs = {
    'rd_rs1_rs2': r'^(?P<rd>\w+)\s*,\s*(?P<rs1>\w+)\s*,\s*(?P<rs2>\w+)$',
    'rd_rs1_imm': r'^(?P<rd>\w+)\s*,\s*(?P<rs1>\w+)\s*,\s*(?P<imm>-?\d+)$',
    'rd_imm': r'^(?P<rd>\w+)\s*,\s*(?P<imm>-?\d+)$',
    'rd_imm(rs1)': r'^(?P<rd>\w+)\s*,\s*(?P<imm>-?\d+)\s*\(\s*(?P<rs1>\w+)\s*\)$',
    'rs2_imm(rs1)': r'^(?P<rs2>\w+)\s*,\s*(?P<imm>-?\d+)\s*\(\s*(?P<rs1>\w+)\s*\)$',
    'rs1_rs2_imm': r'^(?P<rs1>\w+)\s*,\s*(?P<rs2>\w+)\s*,\s*(?P<imm>-?\d+)$',
}

__supported_instructions = [
    InstDef('add', InstType.R_, 0b0110011, 0x0, 0x00, __inst_arg_structs['rd_rs1_rs2']),  # add rd, rs1, rs2
    InstDef('sub', InstType.R_, 0b0110011, 0x0, 0x20, __inst_arg_structs['rd_rs1_rs2']),  # sub rd, rs1, rs2
    InstDef('or', InstType.R_, 0b0110011, 0x6, 0x00, __inst_arg_structs['rd_rs1_rs2']),  # or rd, rs1, rs2
    InstDef('and', InstType.R_, 0b0110011, 0x7, 0x00, __inst_arg_structs['rd_rs1_rs2']),  # and rd, rs1, rs2
    InstDef('slt', InstType.R_, 0b0110011, 0x2, 0x00, __inst_arg_structs['rd_rs1_rs2']),  # slt rd, rs1, rs2
    InstDef('addi', InstType.I_, 0b0010011, 0x0, None, __inst_arg_structs['rd_rs1_imm']),  # addi rd, rs1, imm
    InstDef('ori', InstType.I_, 0b0010011, 0x6, None, __inst_arg_structs['rd_rs1_imm']),  # ori rd, rs1, imm
    InstDef('andi', InstType.I_, 0b0010011, 0x7, None, __inst_arg_structs['rd_rs1_imm']),  # andi rd, rs1, imm
    InstDef('lw', InstType.I_, 0b0000011, 0x2, None, __inst_arg_structs['rd_imm(rs1)']),  # lw rd, imm(rs1)
    InstDef('sw', InstType.S_, 0b0100011, 0x2, None, __inst_arg_structs['rs2_imm(rs1)']),  # sw rs2, imm(rs1)
    InstDef('beq', InstType.B_, 0b1100011, 0x0, None, __inst_arg_structs['rs1_rs2_imm']),  # beq rs1, rs2, imm
    InstDef('jal', InstType.J_, 0b1101111, None, None, __inst_arg_structs['rd_imm']),  # jal rd, imm
    InstDef('jalr', InstType.I_, 0b1100111, 0x0, None, __inst_arg_structs['rd_rs1_imm']),  # jalr rd, rs1, imm
    InstDef('lui', InstType.U_, 0b0110111, None, None, __inst_arg_structs['rd_imm']),  # lui rd, imm
]

supported_inst_dict: Dict[str, InstDef] = {inst.inst: inst for inst in __supported_instructions}


def reg_mapper(reg: str) -> int:
    if reg[0] == 'x':
        if reg[1:].isdigit() and 0 <= int(reg[1:]) < 32:
            return int(reg[1:])
    else:
        match reg:
            case 'zero' | 'ra' | 'sp' | 'gp' | 'tp' | 's0' | 'fp' | 's1':
                return {'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4, 's0': 8, 'fp': 8, 's1': 9}[reg]
            case 't0' | 't1' | 't2':
                return 5 + int(reg[1:])
            case 'a0' | 'a1' | 'a2' | 'a3' | 'a4' | 'a5' | 'a6' | 'a7':
                return 10 + int(reg[1:])
            case 's2' | 's3' | 's4' | 's5' | 's6' | 's7' | 's8' | 's9' | 's10' | 's11':
                return 16 + int(reg[1:])
            case 't3' | 't4' | 't5' | 't6':
                return 25 + int(reg[1:])

    raise ValueError(f'Invalid register: {reg}')
