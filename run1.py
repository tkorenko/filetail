#!/usr/bin/env python2
"""
This is an example of use of FileTail class for efficient tracking recently
added information to a text file.
"""

import filetail


def main():
    # FileTail() Arguments:
    #   arg1      - path to file which we are going to track
    #   state_dir - a directory for state files (CWD is used if omitted)
    #   debug     - (optional) enables printing diagnostic messages
    tailed_file = filetail.FileTail('data/tracked_file', state_dir='junk',
                                    debug=True)

    file_obj = tailed_file.get_file_object()

    lines_qty = 0

    while True:
        line = file_obj.readline()
        if not line:
            # Either tailed file is empty, or we've read it up to its end.
            break
        if len(line) > 0 and line[-1] != '\n':
            # This line is incomplete, lets skip it for now.
            break

        # Remember current read position, we'll start from it next time.
        tailed_file.save_read_pos()

        # Here comes processing (simplified to just printing to the screen)
        line = line.rstrip()
        print '  > %s' % (line)
        lines_qty += 1

    print '  >---\n  Lines read: %d\n  >---' % (lines_qty)


main()
