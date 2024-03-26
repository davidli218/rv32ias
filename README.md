# RISC-V RV32I Assembler

This project provides an assembler for the RISC-V RV32I instruction set.



## Installation

```shell
pip install git+https://github.com/davidli218/rv32ias.git
```



## Usage

To assemble an assembly file into machine code, use the following command:

```shell
rv32ias code.asm
```

### Options

```
-h, --help     show help message and exit
--verbose, -v  Print verbose output
```

### Example

```
❯ rv32ias -v example.asm

  Addr    | Label |   Hex    |               Bin                |      Assembly      
--------- | ----- | -------- | -------------------------------- | -------------------
+00000000 |       | 00000493 | 00000000000000000000010010010011 | addi s1, zero, 0
+00000004 |       | 00A00913 | 00000000101000000000100100010011 | addi s2, zero, 10
+00000008 |       | 00000293 | 00000000000000000000001010010011 | addi t0, zero, 0
+0000000C | loop  | 0122A333 | 00000001001000101010001100110011 | slt  t1, t0, s2
+00000010 |       | 00030863 | 00000000000000110000100001100011 | beq  t1, zero, exit
+00000014 |       | 005484B3 | 00000000010101001000010010110011 | add  s1, s1, t0
+00000018 |       | 00128293 | 00000000000100101000001010010011 | addi t0, t0, 1
+0000001C |       | FF1FF3EF | 11111111000111111111001111101111 | jal  t2, loop
+00000020 | exit  | 000003EF | 00000000000000000000001111101111 | jal  t2, 0
```

