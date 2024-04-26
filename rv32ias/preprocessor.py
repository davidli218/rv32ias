import re
from typing import List, Tuple, Dict

from rv32ias.exceptions import AsmDuplicateLabelError
from rv32ias.exceptions import AsmInvalidInstructionError
from rv32ias.exceptions import AsmInvalidRegisterError
from rv32ias.exceptions import AsmInvalidSyntaxError
from rv32ias.exceptions import AsmUndefinedLabelError
from rv32ias.isa import reg_mapper
from rv32ias.isa import rv32i_inst_dict
from rv32ias.models import AsmCodeLine
from rv32ias.models import AsmCodeLineType
from rv32ias.models import Instruction

__all__ = [
    'AsmParser',
]


class AsmParser:
    def __init__(self, asm_raw: str):
        self.__asm = self.__analyze_asm(asm_raw)

        self.__jump_targets: Dict[str, int] = {}
        self.__parsed_instructions: List[Instruction] = []

        self.__build_jump_table()
        self.__parse_asm()
        self.__validate_registers()

    @staticmethod
    def __analyze_asm(asm_raw: str) -> List[AsmCodeLine]:
        asm = []
        im_ptr = 0

        for i, line in enumerate(asm_raw.split('\n')):
            reduced_line = re.sub(r'^\s*|\s*$', '', line)

            if not line:
                asm.append(AsmCodeLine(AsmCodeLineType.EMPTY, line, reduced_line, 0))
                continue

            if reduced_line[0] == '#':
                asm.append(AsmCodeLine(AsmCodeLineType.COMMENT, line, reduced_line, line.index(reduced_line)))
                continue

            reduced_line = re.sub(r'#.*', '', reduced_line)
            reduced_line = re.sub(r'^\s*|\s*$', '', reduced_line)

            asm.append(
                AsmCodeLine(
                    AsmCodeLineType.LABEL if ':' in reduced_line else AsmCodeLineType.INSTRUCTION,
                    line, reduced_line, line.index(reduced_line), im_ptr
                )
            )

            if ':' not in reduced_line:
                im_ptr += 4

        return asm

    def __build_err_context(self, raw_i: int, e_range: tuple = None, msg='') -> Tuple[int, str, str]:
        if raw_i == 0:
            code_begin_index = 0
            error_line = 0
        elif raw_i == len(self.__asm) - 1:
            code_begin_index = len(self.__asm) - 3
            error_line = 2
        else:
            code_begin_index = raw_i - 1
            error_line = 1

        if e_range is None:
            e_range = (self.__asm[raw_i].clean_offset, len(self.__asm[raw_i].clean))

        code_space = []
        for i, code in enumerate(self.__asm[code_begin_index:code_begin_index + 3]):
            if i == error_line:
                label = 'err!'
                code_a = code.raw[:e_range[0]]
                code_b = code.raw[e_range[0]:sum(e_range)]
                code_c = code.raw[sum(e_range):]
                code = f"{code_a}\033[93m{code_b}\033[0m{code_c}"
                code_space.append(f"\033[91m{label:^6} -> \033[0m{code}")
            else:
                label = code_begin_index + i + 1
                code_space.append(f'\033[90m{label:^6} -> {code}\033[0m')

        return raw_i + 1, '\n'.join(code_space), msg

    def __build_jump_table(self) -> None:
        for i, line in enumerate(self.__asm):
            if line.type == AsmCodeLineType.LABEL:
                re_match = re.match(r'^(?P<label>\w+)\s*:$', line.clean)

                if re_match is None:
                    raise AsmInvalidSyntaxError(*self.__build_err_context(i))

                label = re_match.group('label')

                if label[0].isdigit():
                    error_range = (line.clean_offset, len(label))
                    error_note = 'Label cannot start with a digit'
                    raise AsmInvalidSyntaxError(*self.__build_err_context(i, error_range, error_note))

                if label in self.__jump_targets:
                    error_range = (line.clean_offset, len(label))
                    raise AsmDuplicateLabelError(*self.__build_err_context(i, error_range))

                self.__jump_targets[label] = line.im_ptr

    def __parse_asm(self) -> None:
        for i, line in enumerate(self.__asm):
            if line.type != AsmCodeLineType.INSTRUCTION:
                continue

            # ! Raise when only one word in line
            try:
                inst, args = line.clean.split(maxsplit=1)
            except ValueError:
                error_note = 'Incomplete instruction'
                raise AsmInvalidSyntaxError(*self.__build_err_context(i, msg=error_note))

            # ! Raise when instruction not in RV32I Instruction Dictionary
            if inst not in rv32i_inst_dict:
                error_range = (line.clean_offset, len(inst))
                raise AsmInvalidInstructionError(*self.__build_err_context(i, error_range))

            re_match = re.match(rv32i_inst_dict[inst].inst_arg_re, args)

            # ! Raise when instruction arguments not match
            if re_match is None:
                error_note = 'Invalid instruction arguments'
                raise AsmInvalidSyntaxError(*self.__build_err_context(i, msg=error_note))

            args_dict = re_match.groupdict()

            # Handle immediate
            if 'imm' in args_dict:
                try:
                    args_dict['imm'] = int(args_dict['imm'], 0)
                except ValueError:
                    error_note = 'Invalid immediate value'
                    raise AsmInvalidSyntaxError(*self.__build_err_context(i, msg=error_note))

            # Handle label
            if 'label' in args_dict:
                if (label := args_dict.pop('label')) in self.__jump_targets:
                    args_dict['imm'] = self.__jump_targets[label] - line.im_ptr
                else:
                    raise AsmUndefinedLabelError(*self.__build_err_context(i))

            self.__parsed_instructions.append(Instruction(line_num=i, inst=inst, **args_dict))

    def __validate_registers(self) -> None:
        for i, inst in enumerate(self.__parsed_instructions):
            try:
                reg_mapper(inst.rd if inst.rd is not None else 'zero')
                reg_mapper(inst.rs1 if inst.rs1 is not None else 'zero')
                reg_mapper(inst.rs2 if inst.rs2 is not None else 'zero')
            except ValueError:
                raise AsmInvalidRegisterError(*self.__build_err_context(inst.line_num))

    @property
    def asm(self) -> List[AsmCodeLine]:
        return self.__asm

    @property
    def jump_table(self) -> Dict[str, int]:
        return self.__jump_targets

    @property
    def instructions(self) -> List[Instruction]:
        return self.__parsed_instructions
