from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

__all__ = [
    'InstType',
    'rv32i_inst_dict',
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


__arg_re = {
    'rd': r'(?P<rd>\w+)',
    'rs1': r'(?P<rs1>\w+)',
    'rs2': r'(?P<rs2>\w+)',
    'imm': r'(?P<imm>-?\w+)',
    'label': r'(?P<label>\w+)',
}

__inst_arg_structs = {
    'rd_rs1_rs2': rf'^{__arg_re["rd"]}\s*,\s*{__arg_re["rs1"]}\s*,\s*{__arg_re["rs2"]}$',
    'rd_rs1_imm': rf'^{__arg_re["rd"]}\s*,\s*{__arg_re["rs1"]}\s*,\s*{__arg_re["imm"]}$',
    'rd_imm': rf'^{__arg_re["rd"]}\s*,\s*{__arg_re["imm"]}$',
    'rd_imm(rs1)': rf'^{__arg_re["rd"]}\s*,\s*{__arg_re["imm"]}\({__arg_re["rs1"]}\)$',
    'rs2_imm(rs1)': rf'^{__arg_re["rs2"]}\s*,\s*{__arg_re["imm"]}\({__arg_re["rs1"]}\)$',
    'rd_label': rf'^{__arg_re["rd"]}\s*,\s*{__arg_re["label"]}$',
    'rs1_rs2_label': rf'^{__arg_re["rs1"]}\s*,\s*{__arg_re["rs2"]}\s*,\s*{__arg_re["label"]}$',
    'rd_rs1_label': rf'^{__arg_re["rd"]}\s*,\s*{__arg_re["rs1"]}\s*,\s*{__arg_re["label"]}$',
}

__rv32i_instructions = [
    # Group 1: Register compute instructions [0b0110011]
    InstDef('add', InstType.R_, 0b0110011, 0x0, 0x00, __inst_arg_structs['rd_rs1_rs2']),
    InstDef('sub', InstType.R_, 0b0110011, 0x0, 0x20, __inst_arg_structs['rd_rs1_rs2']),
    InstDef('xor', InstType.R_, 0b0110011, 0x4, 0x00, __inst_arg_structs['rd_rs1_rs2']),
    InstDef('or', InstType.R_, 0b0110011, 0x6, 0x00, __inst_arg_structs['rd_rs1_rs2']),
    InstDef('and', InstType.R_, 0b0110011, 0x7, 0x00, __inst_arg_structs['rd_rs1_rs2']),
    InstDef('sll', InstType.R_, 0b0110011, 0x1, 0x00, __inst_arg_structs['rd_rs1_rs2']),
    InstDef('srl', InstType.R_, 0b0110011, 0x5, 0x00, __inst_arg_structs['rd_rs1_rs2']),
    InstDef('sra', InstType.R_, 0b0110011, 0x5, 0x20, __inst_arg_structs['rd_rs1_rs2']),
    InstDef('slt', InstType.R_, 0b0110011, 0x2, 0x00, __inst_arg_structs['rd_rs1_rs2']),
    InstDef('sltu', InstType.R_, 0b0110011, 0x3, 0x00, __inst_arg_structs['rd_rs1_rs2']),
    # Group 2: Immediate compute instructions [0b0010011]
    InstDef('addi', InstType.I_, 0b0010011, 0x0, None, __inst_arg_structs['rd_rs1_imm']),
    InstDef('xori', InstType.I_, 0b0010011, 0x4, None, __inst_arg_structs['rd_rs1_imm']),
    InstDef('ori', InstType.I_, 0b0010011, 0x6, None, __inst_arg_structs['rd_rs1_imm']),
    InstDef('andi', InstType.I_, 0b0010011, 0x7, None, __inst_arg_structs['rd_rs1_imm']),
    InstDef('slli', InstType.I_, 0b0010011, 0x1, 0x00, __inst_arg_structs['rd_rs1_imm']),
    InstDef('srli', InstType.I_, 0b0010011, 0x5, 0x00, __inst_arg_structs['rd_rs1_imm']),
    InstDef('srai', InstType.I_, 0b0010011, 0x5, 0x20, __inst_arg_structs['rd_rs1_imm']),
    InstDef('slti', InstType.I_, 0b0010011, 0x2, None, __inst_arg_structs['rd_rs1_imm']),
    InstDef('sltiu', InstType.I_, 0b0010011, 0x3, None, __inst_arg_structs['rd_rs1_imm']),
    # Group 3: Load from memory instructions [0b0000011]
    InstDef('lb', InstType.I_, 0b0000011, 0x0, None, __inst_arg_structs['rd_imm(rs1)']),
    InstDef('lh', InstType.I_, 0b0000011, 0x1, None, __inst_arg_structs['rd_imm(rs1)']),
    InstDef('lw', InstType.I_, 0b0000011, 0x2, None, __inst_arg_structs['rd_imm(rs1)']),
    InstDef('lbu', InstType.I_, 0b0000011, 0x4, None, __inst_arg_structs['rd_imm(rs1)']),
    InstDef('lhu', InstType.I_, 0b0000011, 0x5, None, __inst_arg_structs['rd_imm(rs1)']),
    # Group 4: Store to memory instructions [0b0100011]
    InstDef('sb', InstType.S_, 0b0100011, 0x0, None, __inst_arg_structs['rs2_imm(rs1)']),
    InstDef('sh', InstType.S_, 0b0100011, 0x1, None, __inst_arg_structs['rs2_imm(rs1)']),
    InstDef('sw', InstType.S_, 0b0100011, 0x2, None, __inst_arg_structs['rs2_imm(rs1)']),
    # Group 5: Branch instructions [0b1100011]
    InstDef('beq', InstType.B_, 0b1100011, 0x0, None, __inst_arg_structs['rs1_rs2_label']),
    InstDef('bne', InstType.B_, 0b1100011, 0x1, None, __inst_arg_structs['rs1_rs2_label']),
    InstDef('blt', InstType.B_, 0b1100011, 0x4, None, __inst_arg_structs['rs1_rs2_label']),
    InstDef('bge', InstType.B_, 0b1100011, 0x5, None, __inst_arg_structs['rs1_rs2_label']),
    InstDef('bltu', InstType.B_, 0b1100011, 0x6, None, __inst_arg_structs['rs1_rs2_label']),
    InstDef('bgeu', InstType.B_, 0b1100011, 0x7, None, __inst_arg_structs['rs1_rs2_label']),
    # Group 6: Jump instructions [0b1101111/0b1100111]
    InstDef('jal', InstType.J_, 0b1101111, None, None, __inst_arg_structs['rd_label']),
    InstDef('jalr', InstType.I_, 0b1100111, 0x0, None, __inst_arg_structs['rd_rs1_label']),
    # Group 7: Load upper immediate instructions [0b0110111]
    InstDef('lui', InstType.U_, 0b0110111, None, None, __inst_arg_structs['rd_imm']),
]

rv32i_inst_dict: Dict[str, InstDef] = {inst.inst: inst for inst in __rv32i_instructions}


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
