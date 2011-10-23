#! /usr/bin/env python
"""
Eliminate reads with minimum k-mer abundance higher than
DESIRED_COVERAGE.  Output sequences will be placed in 'infile.keep'.

% python scripts/normalize-by-min.py [ -C <cutoff> ] <data1> <data2> ...

Use '-h' for parameter help.
"""

import sys, screed, os
import khmer
from khmer.counting_args import build_construct_args, DEFAULT_MIN_HASHSIZE

DEFAULT_MINIMUM_COVERAGE=5

def main():
    parser = build_construct_args()
    parser.add_argument('-C', '--cutoff', type=int, dest='cutoff',
                        default=DEFAULT_MINIMUM_COVERAGE)
    parser.add_argument('-s', '--savehash', dest='savehash', default='')
    parser.add_argument('-l', '--loadhash', dest='loadhash',
                        default='')
    parser.add_argument('input_filenames', nargs='+')

    args = parser.parse_args()

    if not args.quiet:
        if args.min_hashsize == DEFAULT_MIN_HASHSIZE:
            print>>sys.stderr, "** WARNING: hashsize is default!  You absodefly want to increase this!\n** Please read the docs!"

        print>>sys.stderr, '\nPARAMETERS:'
        print>>sys.stderr, ' - kmer size =    %d \t\t(-k)' % args.ksize
        print>>sys.stderr, ' - n hashes =     %d \t\t(-N)' % args.n_hashes
        print>>sys.stderr, ' - min hashsize = %-5.2g \t(-x)' % args.min_hashsize
        print>>sys.stderr, ''
        print>>sys.stderr, 'Estimated memory usage is %.2g bytes (n_hashes x min_hashsize)' % (args.n_hashes * args.min_hashsize)
        print>>sys.stderr, '-'*8

    K=args.ksize
    HT_SIZE=args.min_hashsize
    N_HT=args.n_hashes
    DESIRED_COVERAGE=args.cutoff

    filenames = args.input_filenames

    if args.loadhash:
        print 'loading hashtable from', args.loadhash
        ht = khmer.load_counting_hash(args.loadhash)
    else:
        print 'making hashtable'
        ht = khmer.new_counting_hash(K, HT_SIZE, N_HT)

    total = 0
    discarded = 0
    for input_filename in filenames:
        output_name = os.path.basename(input_filename) + '.keep'
        outfp = open(output_name, 'w')

        for n, record in enumerate(screed.open(input_filename)):
            if n > 0 and n % 10000 == 0:
                print '... kept', total - discarded, 'of', total, ', or', \
                    int(100. - discarded / float(total) * 100.), '%'
                print '... in file', input_filename

            total += 1

            if len(record.sequence) < K:
                continue

            seq = record.sequence.replace('N', 'A')
            mincount = ht.get_min_count(seq)

            if mincount < DESIRED_COVERAGE:
                ht.consume(seq)
                outfp.write('>%s\n%s\n' % (record.name, record.sequence))
            else:
                discarded += 1

        print 'DONE with', input_filename, '; kept', total - discarded, 'of',\
            total, 'or', int(100. - discarded / float(total) * 100.), '%'
        print 'output in', output_name

    if args.savehash:
        print 'Saving hashfile through', input_filename
        print '...saving to', args.savehash
        ht.save(args.savehash)

if __name__ == '__main__':
    main()