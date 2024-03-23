# sum of 0 to 9

    addi s0, zero, 0     # sum = 0
    addi s1, zero, 10    # n = 10
    addi t0, zero, 0     # counter = 0

# loop start
    slt  t1, s1,   t0    # if (n - counter) == 0
    beq  t1, zero, 16    #     break;
    add  s0, s0,   t0    # sum += counter
    addi t0, t0,   1     # counter++;
    jal  t2, -16         # continue;
# loop end

    jal  t2, 0           # exit program
