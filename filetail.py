#!/usr/bin/env python2

import copy
import hashlib
import json
import os
import sys


class FileTail(object):
    def __init__(self, file_name, state_dir='.', debug=False):
        self._data = None
        self._debug = debug
        self._file_object = None
        self._state = None
        self._tailed_file = file_name

        # If input file does not exist, we've nothing to work upon.
        if not os.path.isfile(self._tailed_file):
            raise ValueError

        self._state_file = self._mk_state_fname(state_dir)

        tf_stat = os.stat(self._tailed_file)

        # Check if state file exists.
        if not os.path.isfile(self._state_file):
            self.dbgout('state file not found, making one')

            self._init_state(tf_stat.st_ino)
            self._save_state()

            self.dbgout('  done: %s' % (self._state_file))
        else:
            self.dbgout('loading state from %s' % (self._state_file))
            self._load_state()

            # Check whether saved state corresponds to the current file.
            if (tf_stat.st_ino != self._state['inode'] or
                    tf_stat.st_size < self._state['read_pos']):
                # Saved state does not correspond to the file in question.
                self.dbgout('  state: %s' % (
                                json.dumps(self._state, sort_keys=True)))
                self.dbgout('skipping state: inodes do not match'
                            ' or read_pos is invalid.')
                self._init_state(tf_stat.st_ino)
                self._save_state()

        self.dbgout('  state: %s' % (json.dumps(self._state, sort_keys=True)))

        self._data = self._state['opaque']

        # Open for read...
        f_obj = open(self._tailed_file, 'r')
        # NOTE: it is acceptable to die here in case of any exceptions
        # during open() call.

        # ... + rewind to read_pos ('0' means SEEK_SET here)
        f_obj.seek(self._state['read_pos'], 0)

        self._file_object = f_obj


    def __del__(self):
        if self._state is not None:
            self.dbgout('saving  state to   %s' % (self._state_file))
            self.dbgout('  state: %s' % (
                            json.dumps(self._state, sort_keys=True)))
            self._save_state()
            self._file_object.close()


    def _mk_state_fname(self, state_dir):
        hm = hashlib.md5()
        hm.update(self._tailed_file)
        return '%s/%s.tailf-state' % (state_dir, hm.hexdigest())


    def _init_state(self, inode_num):
        self._state = {
            'inode': inode_num,
            'read_pos': 0,
            'opaque': None
        }


    def _save_state(self):
        self._state['opaque'] = self._data

        curr_fname = '%s_' % (self._state_file)

        with open(curr_fname, 'w') as f_obj:
            json.dump(self._state, f_obj)
        os.rename(curr_fname, self._state_file)


    def _load_state(self):
        with open(self._state_file, 'r') as f_obj:
            js = json.load(f_obj)
            jk = js.keys()
            # Check if content is as expected.
            if 'inode' in jk and 'read_pos' in jk and 'opaque' in jk:
                self._state = js
            else:
                self._init_state()


    def save_read_pos(self):
        old_pos = self._state['read_pos']
        self._state['read_pos'] = self._file_object.tell()
        self.dbgout('read_pos advaned: %d -> %d' % (
                        old_pos, self._state['read_pos']))


    def get_file_object(self):
        return self._file_object


    def get_opaque(self):
        return copy.deepcopy(self._data)


    def set_opaque(self, data):
        self._data = copy.deepcopy(data)


    def dbgout(self, msg):
        if self._debug:
            sys.stderr.write('DBG: %s\n' % msg)
