# RISC-V RV32I Assembler

This project provides an assembler for the RISC-V RV32I instruction set.



## Installation

```shell
pip install git+https://github.com/davidli218/rv32ias.git
```



## Usage

```
rv32ias [-h] [--binary] [--output OUTPUT]
        [--verbose] [--pretty PRETTY]
        asm_file

positional arguments:
  asm_file              Assembly file to be assembled

options:
  -h, --help            show this help message and exit
  --binary, -b          Output binary instead of hex
  --output OUTPUT, -o OUTPUT
                        Save output to a file
  --verbose, -v         Print verbose output
  --pretty PRETTY, -p PRETTY
                        Pretty print verbose output
```



### Examples

1. Print machine code

   ```
   ❯ rv32ias example.asm
   
   00000493
   00A00913
   00000293
   0122A333
   00030863
   005484B3
   00128293
   FF1FF3EF
   000003EF
   ```

   ```
   ❯ rv32ias -b example.asm
   
   00000000000000000000010010010011
   00000000101000000000100100010011
   00000000000000000000001010010011
   00000001001000101010001100110011
   00000000000000110000100001100011
   00000000010101001000010010110011
   00000000000100101000001010010011
   11111111000111111111001111101111
   00000000000000000000001111101111
   ```

   

2. Print verbose output

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
   
   ```
   ❯ rv32ias -v -p full example.asm 
   
     Addr    | Label |   Hex    |               Bin                |                          Assembly                         
   --------- | ----- | -------- | -------------------------------- | ----------------------------------------------------------
       *     |       |    *     |                *                 | # sum of 0 to 9                                           
       *     |       |    *     |                *                 |                                                           
   +00000008 |       | 00000493 | 00000000000000000000010010010011 |     addi s1, zero, 0     # sum = 0                        
   +00000012 |       | 00A00913 | 00000000101000000000100100010011 |     addi s2, zero, 10    # n = 10                         
   +00000016 |       | 00000293 | 00000000000000000000001010010011 |     addi t0, zero, 0     # counter = 0                    
       *     |       |    *     |                *                 |                                                           
       *     |       |    *     |                *                 | loop:                                                     
   +00000028 | loop  | 0122A333 | 00000001001000101010001100110011 |     slt  t1, t0,   s2    # comp_result = n < counter      
   +00000032 |       | 00030863 | 00000000000000110000100001100011 |     beq  t1, zero, exit  # if comp_result == 0, brake loop
   +00000036 |       | 005484B3 | 00000000010101001000010010110011 |     add  s1, s1,   t0    # sum += counter                 
   +00000040 |       | 00128293 | 00000000000100101000001010010011 |     addi t0, t0,   1     # counter++                      
   +00000044 |       | FF1FF3EF | 11111111000111111111001111101111 |     jal  t2, loop        # continue                       
       *     |       |    *     |                *                 |                                                           
       *     |       |    *     |                *                 | exit:                                                     
   +00000056 | exit  | 000003EF | 00000000000000000000001111101111 |     jal  t2, exit        # exit                           
       *     |       |    *     |                *                 |                                                           
   ```
