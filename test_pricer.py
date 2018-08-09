with open('pricer.out.10000') as sample_output, open('output10000.txt') as output:
    for line1, line2 in zip(sample_output, output):
        if line1 != line2:
            print 'Mismatch:\n', line1, line2
            print ""