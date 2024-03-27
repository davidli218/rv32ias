class AsmInvalidSyntaxError(Exception):
    def __init__(self, i: int, code_space: str) -> None:
        super().__init__(f"Syntax Error found at line {i}\n{code_space}")


class AsmDuplicateLabelError(Exception):
    def __init__(self, i: int, code_space: str) -> None:
        super().__init__(f"Duplicate Label found at line {i}\n{code_space}")


class AsmUndefinedLabelError(Exception):
    def __init__(self, i: int, code_space: str) -> None:
        super().__init__(f"Undefined Label found at line {i}\n{code_space}")


class AsmInvalidInstructionError(Exception):
    def __init__(self, i: int, code_space: str) -> None:
        super().__init__(f"Invalid Instruction found at line {i}\n{code_space}")


class AsmInvalidRegisterError(Exception):
    def __init__(self, i: int, code_space: str) -> None:
        super().__init__(f"Invalid Register found at line {i}\n{code_space}")
