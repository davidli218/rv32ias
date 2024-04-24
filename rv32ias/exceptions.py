class AsmParseError(Exception):
    error_type = 'Unknown'

    def __init__(self, i: int, code_space: str) -> None:
        super().__init__(f"{self.error_type} Error: found at line {i}\n{code_space}")


class AsmInvalidSyntaxError(AsmParseError):
    error_type = 'Syntax'


class AsmDuplicateLabelError(AsmParseError):
    error_type = 'Duplicate Label'


class AsmUndefinedLabelError(AsmParseError):
    error_type = 'Undefined Label'


class AsmInvalidInstructionError(AsmParseError):
    error_type = 'Invalid Instruction'


class AsmInvalidRegisterError(AsmParseError):
    error_type = 'Invalid Register'
