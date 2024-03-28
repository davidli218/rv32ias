import re
from typing import List, Dict, Final

from rv32ias.exceptions import AsmDuplicateLabelError
from rv32ias.exceptions import AsmInvalidInstructionError
from rv32ias.exceptions import AsmInvalidRegisterError
from rv32ias.exceptions import AsmInvalidSyntaxError
from rv32ias.exceptions import AsmUndefinedLabelError
from rv32ias.isa import reg_mapper
from rv32ias.isa import rv32i_inst_dict
from rv32ias.models import Instruction

__all__ = [
    'AsmParser',
]


class AsmParser:
    def __init__(self, asm_raw: str):
        self.__asm_raw_lines: Final[List[str]] = asm_raw.split('\n')

        self.__jump_targets: Dict[str, int] = {}
        self.__asm_clean_lines: List[str] = []
        self.__asm_clean_lines_raw_index: List[int] = []
        self.__parsed_instructions: List[Instruction] = []

        self.__do_preprocess()
        self.__parse_asm()
        self.__validate_registers()

    def __build_err_context(self, raw_index: int) -> (int, str):
        if raw_index == 0:
            code_begin_index = 0
            error_line = 0
        elif raw_index == len(self.__asm_raw_lines) - 1:
            code_begin_index = len(self.__asm_raw_lines) - 3
            error_line = 2
        else:
            code_begin_index = raw_index - 1
            error_line = 1

        code_space = ''
        for i, code in enumerate(self.__asm_raw_lines[code_begin_index:code_begin_index + 3]):
            label = f"{'err!' if i == error_line else str(code_begin_index + i)}"
            code_space += f'{label:^6} -> {code}\n'

        return raw_index, code_space[:-1]

    def __do_preprocess(self) -> None:
        for i, line in enumerate(self.__asm_raw_lines):
            # Remove comments
            line = re.sub(r'#.*', '', line)

            # Remove leading and trailing whitespaces
            line = re.sub(r'^\s*|\s*$', '', line)

            # If line is comment or empty, skip
            if not line:
                continue

            # If line is label, add to jump_targets
            if ':' in line:
                re_match = re.match(r'^(?P<label>\w+)\s*:', line)

                if re_match is None:
                    raise AsmInvalidSyntaxError(*self.__build_err_context(i))

                label = re_match.group('label')

                if label[0].isdigit():
                    raise AsmInvalidSyntaxError(*self.__build_err_context(i))

                if label in self.__jump_targets:
                    raise AsmDuplicateLabelError(*self.__build_err_context(i))

                self.__jump_targets[label] = 4 * len(self.__asm_clean_lines)
                continue

            # Remove whitespaces around commas
            line = re.sub(r'\s*,\s*', ', ', line)

            # Remove whitespaces around parentheses
            line = re.sub(r'\s*\(\s*', '(', line)
            line = re.sub(r'\s*\)', ')', line)

            self.__asm_clean_lines.append(line)
            self.__asm_clean_lines_raw_index.append(i)

    def __parse_asm(self) -> None:
        for i, line in enumerate(self.__asm_clean_lines):
            raw_index = self.__asm_clean_lines_raw_index[i]

            # ! Raise when only one word in line
            try:
                inst, args = line.split(maxsplit=1)
            except ValueError:
                raise AsmInvalidSyntaxError(*self.__build_err_context(raw_index))

            # ! Raise when instruction not in RV32I Instruction Dictionary
            if inst not in rv32i_inst_dict:
                raise AsmInvalidInstructionError(*self.__build_err_context(raw_index))

            re_match = re.match(rv32i_inst_dict[inst].inst_arg_re, args)

            # ! Raise when instruction arguments not match
            if re_match is None:
                raise AsmInvalidSyntaxError(*self.__build_err_context(raw_index))

            args_dict = re_match.groupdict()

            # Handle label
            if 'label' in args_dict:
                if (label := args_dict.pop('label')) in self.__jump_targets:
                    args_dict['imm'] = self.__jump_targets[label] - 4 * i
                else:
                    raise AsmUndefinedLabelError(*self.__build_err_context(raw_index))

            self.__parsed_instructions.append(Instruction(line, inst, **args_dict))

    def __validate_registers(self) -> None:
        for i, inst in enumerate(self.__parsed_instructions):
            raw_index = self.__asm_clean_lines_raw_index[i]
            try:
                reg_mapper(inst.rd if inst.rd is not None else 'zero')
                reg_mapper(inst.rs1 if inst.rs1 is not None else 'zero')
                reg_mapper(inst.rs2 if inst.rs2 is not None else 'zero')
            except ValueError:
                raise AsmInvalidRegisterError(*self.__build_err_context(raw_index))

    @property
    def asm_raw(self) -> str:
        return '\n'.join(self.__asm_raw_lines)

    @property
    def asm_clean(self) -> str:
        output = []

        for line in self.__asm_clean_lines:
            if ':' in line:
                output.append(f'{line}')
            else:
                output.append(f'    {line}')

        return '\n'.join(output)

    @property
    def jump_table(self) -> Dict[str, int]:
        return self.__jump_targets

    @property
    def instructions(self) -> List[Instruction]:
        return self.__parsed_instructions
