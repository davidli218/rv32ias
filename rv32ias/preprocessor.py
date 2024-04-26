import re
from typing import List, Tuple, Dict

from rv32ias.exceptions import AsmDuplicateLabelError
from rv32ias.exceptions import AsmInvalidInstructionError
from rv32ias.exceptions import AsmInvalidRegisterError
from rv32ias.exceptions import AsmInvalidSyntaxError
from rv32ias.exceptions import AsmUndefinedLabelError
from rv32ias.isa import reg_mapper
from rv32ias.isa import rv32i_inst_dict
from rv32ias.models import AsmLine
from rv32ias.models import AsmLineType
from rv32ias.models import Instruction


class AsmParser:
    def __init__(self, asm_raw: str):
        self.__asm: List[AsmLine] = self.__analyze_asm(asm_raw)

        self.__jump_targets: Dict[str, int] = {}
        self.__parsed_instructions: List[Instruction] = []

        self.__build_jump_table()
        self.__parse_asm()

    @staticmethod
    def __analyze_asm(asm_raw: str) -> List[AsmLine]:
        asm = []
        im_ptr = 0

        for i, line in enumerate(asm_raw.split('\n')):
            reduced_line = re.sub(r'^\s*|\s*$', '', line)
            ctx_offset = line.index(reduced_line)

            if not line:
                asm.append(AsmLine(i, AsmLineType.EMPTY, line, reduced_line, ctx_offset, im_ptr))
                continue

            if reduced_line[0] == '#':
                asm.append(AsmLine(i, AsmLineType.COMMENT, line, reduced_line, ctx_offset, im_ptr))
                continue

            reduced_line = re.sub(r'\s*#.*$', '', reduced_line)

            if re.match(r'^\w+\s*:$', reduced_line):
                asm.append(AsmLine(i, AsmLineType.LABEL, line, reduced_line, ctx_offset, im_ptr))
            else:
                asm.append(AsmLine(i, AsmLineType.INSTRUCTION, line, reduced_line, ctx_offset, im_ptr))
                im_ptr += 4

        return asm

    def __build_err_ctx(self, raw_i: int, span: tuple = None, note='') -> Tuple[int, str, str]:
        if raw_i == 0:
            code_begin_index = 0
            error_line = 0
        elif raw_i == len(self.asm) - 1:
            code_begin_index = len(self.asm) - 3
            error_line = 2
        else:
            code_begin_index = raw_i - 1
            error_line = 1

        if span is None:
            span = (0, len(self.asm[raw_i].clean))

        code_space = []
        for i, code in enumerate(self.asm[code_begin_index:code_begin_index + 3]):
            if i == error_line:
                label = 'err!'
                offset = self.asm[raw_i].clean_offset
                code_a = code.raw[:offset + span[0]]
                code_b = code.raw[offset + span[0]:offset + sum(span)]
                code_c = code.raw[offset + sum(span):]
                code = f"{code_a}\033[43m{code_b}\033[0m{code_c}"
                code_space.append(f"\033[91m{label:^6} -> \033[0m{code}")
            else:
                label = code_begin_index + i + 1
                code_space.append(f'\033[90m{label:^6} -> {code}\033[0m')

        return raw_i + 1, '\n'.join(code_space), note

    def __build_jump_table(self) -> None:
        for line in (i for i in self.asm if i.type == AsmLineType.LABEL):
            label = line.clean[:-1]

            if not label[0].isalpha():
                span, note = (0, len(label)), 'Label must start with alphabet'
                raise AsmInvalidSyntaxError(*self.__build_err_ctx(line.idx, span, note))

            if label in self.__jump_targets:
                span, note = (0, len(label)), 'Duplicate label found'
                raise AsmDuplicateLabelError(*self.__build_err_ctx(line.idx, span, note))

            self.__jump_targets[label] = line.im_ptr

    def __parse_asm(self) -> None:
        for line in (i for i in self.asm if i.type == AsmLineType.INSTRUCTION):
            # ! Raise when only one word in line
            try:
                inst, args = line.clean.split(maxsplit=1)
            except ValueError:
                raise AsmInvalidSyntaxError(*self.__build_err_ctx(line.idx, note='Incomplete instruction'))

            # ! Raise when instruction not in RV32I Instruction Dictionary
            if inst not in rv32i_inst_dict:
                span, note = (0, len(inst)), f'Instruction `{inst}` not supported'
                raise AsmInvalidInstructionError(*self.__build_err_ctx(line.idx, span, note))

            re_match = re.match(rv32i_inst_dict[inst].inst_arg_re, args)
            args_offset = line.clean.index(args)

            # ! Raise when instruction arguments not match
            if re_match is None:
                span, note = (args_offset, len(args)), 'Invalid instruction arguments'
                raise AsmInvalidSyntaxError(*self.__build_err_ctx(line.idx, span, note))

            args_dict = re_match.groupdict()
            args_pos = {k: args_offset + re_match.span(k)[0] for k in args_dict.keys()}

            # Handle immediate
            if 'imm' in args_dict:
                try:
                    args_dict['imm'] = int(args_dict['imm'], 0)
                except ValueError:
                    span, note = (args_pos['imm'], len(args_dict['imm'])), 'Invalid immediate value'
                    raise AsmInvalidSyntaxError(*self.__build_err_ctx(line.idx, span, note))

            # Handle label
            if 'label' in args_dict:
                if (label := args_dict.pop('label')) in self.__jump_targets:
                    args_dict['imm'] = self.__jump_targets[label] - line.im_ptr
                else:
                    span, note = (args_pos['label'], len(label)), 'Undefined label'
                    raise AsmUndefinedLabelError(*self.__build_err_ctx(line.idx, span, note))

            # ! Raise when invalid register
            for reg_name in ['rd', 'rs1', 'rs2']:
                if reg_name in args_dict:
                    try:
                        reg_mapper(args_dict[reg_name])
                    except ValueError:
                        span, note = (args_pos[reg_name], len(args_dict[reg_name])), 'Invalid register'
                        raise AsmInvalidRegisterError(*self.__build_err_ctx(line.idx, span, note))

            self.__parsed_instructions.append(Instruction(line.idx, inst, **args_dict))

    @property
    def asm(self) -> List[AsmLine]:
        return self.__asm

    @property
    def jump_table(self) -> Dict[str, int]:
        return self.__jump_targets

    @property
    def instructions(self) -> List[Instruction]:
        return self.__parsed_instructions
