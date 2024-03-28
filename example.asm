# sum of 0 to 9

    addi s1, zero, 0     # sum = 0
    addi s2, zero, 10    # n = 10
    addi t0, zero, 0     # counter = 0

loop:
    slt  t1, t0,   s2    # comp_result = n < counter
    beq  t1, zero, exit  # if comp_result == 0, brake loop
    add  s1, s1,   t0    # sum += counter
    addi t0, t0,   1     # counter++
    jal  t2, loop        # continue

exit:
    jal  t2, exit        # exit
