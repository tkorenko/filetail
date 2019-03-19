#!/usr/bin/env python2
"""
This is an example of use of FileTail for passing information from invocation
to invocation.
"""

import time

import filetail


def main():
    # FileTail() Arguments:
    #   arg1      - path to file which we are going to track
    #   state_dir - a directory for state files (CWD is used if omitted)
    #   debug     - (optional) enables printing diagnostic messages
    tailed_file = filetail.FileTail('run2.py', state_dir='junk', debug=False)

    data = tailed_file.get_opaque()

    # An example of usage of saved opaque object is:
    print '  Recovered from previous invocation:'
    print ' ', data

    if data is None:
        data = { }

    data['last_call'] = str(time.strftime('%c'))

    print '\n  Current run is saving the following:'
    print ' ', data

    # Save updated opaque object for the next script invocation:
    tailed_file.set_opaque(data)


main()
