# sum of 0 to 9

    addi s1, zero, 0     # sum = 0
    addi s2, zero, 10    # n = 10
    addi t0, zero, 0     # counter = 0

# loop start
    slt  t1, t0,   s2    # comp_result = n < counter
    beq  t1, zero, 16    # if comp_result == 0, brake loop
    add  s1, s1,   t0    # sum += counter
    addi t0, t0,   1     # counter++;
    jal  t2, -16         # continue;
# loop end

    jal  t2, 0           # exit program
