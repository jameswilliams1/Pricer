with open('pricer.out.200') as sample_output, open('output200.txt') as output:
    for line1, line2 in zip(sample_output, output):
        if line1 != line2:
            print 'Mismatch:\n', line1, line2
            print ""