with open('pricer.out.1') as sample_output, open('output1.txt') as output:
    for line1, line2 in zip(sample_output, output):
        if line1 != line2:
            print 'Mismatch:\n', line1, line2
            print ""