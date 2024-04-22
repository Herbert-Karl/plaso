# -*- coding: utf-8 -*-
"""Parser system accounting files on OpenBSD."""

import math
import os
import re

from plaso.lib import errors
from plaso.parsers import interface
from plaso.parsers import manager

class OpenBSDSystemAccountingParser(interface.FileObjectParser):
  """Parser for system accounting files created on OpenBSD."""

  NAME = "openbsd_system_accounting"
  DATA_FORMAT = "system accounting file"
  
  _MINIMUM_FILE_SIZE = 64 # one structure in the system accounting file is 64 bytes large; any file with entries needs to be at least one structure large, else parsing would make no sense
  
  _FILENAME_FORMAT = re.compile(r'acct(\..*)?') # regex, meant to match the default file "acct" as well as any rotations ("acct.0" to "acct.3" in standard configuration)

  _AHZ = 64 # granularity of data encoding in "comp_t" fields
  _SECSPERHOUR = 3600
  _SECSPERMIN = 60

  # based on https://man.openbsd.org/acct.5
  _ACCOUNTING_FLAGS = {
    0x001: 'fork but not exec',
    0x004: 'system call or stack mapping violation',
    0x008: 'dumped core',
    0x010: 'killed by a signal',
    0x020: 'killed due to pledge violation',
    0x040: 'memory access violation',
    0x080: 'unveil access violation',
    0x200: 'killed by syscall pin violation',
    0x400: 'BT CFI violation'
  }

  # based on https://man.openbsd.org/acct.5
  _STRUCT_FORMAT = '24sHHHHQIIIiII' # see https://docs.python.org/3/library/struct.html#format-characters for meaning
  
  _TEXT_ENCODING = 'iso-8859-1'

  def _Convert_comp_t(self, comp_t):
    """converts the type comp_t used in multiple places in the data structure to the actual units"""
    converted_t = comp_t & 0x1fff  # hex 0x1fff is equivalent to octal 017777 from the referenced C code
    comp_t >>= 13
    while comp_t:
        comp_t -= 1
        converted_t <<= 3
    converted_t = converted_t / self._AHZ # "unit" conversion
    return converted_t 

  def _TimeConverstion(self, total_secs):
    """Helper function to format execution times as a nice string"""
    hours = total_secs / self._SECSPERHOUR
    minutes = math.fmod(total_secs, self._SECSPERHOUR) / self._SECSPERMIN
    seconds = math.fmod(total_secs, self._SECSPERMIN)
    time_string = f"{hours:02.0f}:{minutes:02.0f}:{seconds:05.2f}"
    return time_string

  def _ParseStructFlags(self, flags_value):
    """Helper function to convert the flag values of a struct into somewhat readable names"""
    set_flags = []
    for flag_bit, description in self._ACCOUNTING_FLAGS.items():
        if flags_value & flag_bit:
            set_flags.append(description)
    flags_string = ', '.join(set_flags)
    return flags_string

  def ParseFileObject(self, parser_mediator, file_object):
    """ Parser for system accounting file created by OpenBSD.
    
    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfVFS.
      file_object (dfvfs.FileIO): a file-like object to parse.

    Raises:
      WrongParser: when the file cannot be parsed.
    """
    filename = parser_mediator.GetFilename()
    if (not self._FILENAME_FORMAT.match(filename)):
      raise errors.WrongParser('Not a system accounting file (based on filename).')
    
    file_object.seek(0, os.SEEK_SET)
    
    # TODO: logic!
    _STRUCT_SIZE = struct.calcsize(self._STRUCT_FORMAT)
    try:
        with open(file_path, 'rb') as file: # Opening the file in binary mode
            accounting_structs = []
            while True:
                encoded_data = file.read(_STRUCT_SIZE)
                if not encoded_data:
                    break
                # decode data 
                decoded_data = struct.unpack(struct_format, encoded_data)
                command_name, user_time, system_time, elapsed_time, count_io_blocks, starting_time, user_id, group_id, avg_mem_usage, controlling_tty, process_id, flags = decoded_data
                # further decoding of values
                command_name = command_name.split(b'\x00')[0].decode(self._TEXT_ENCODING)
                starting_time = datetime.datetime.utcfromtimestamp(starting_time).isoformat() + 'Z' # the value for starting_time stored with accounting is calculated from nanoboottime() (meaning the UTC timestamp that the system got booted) and the process associated value from nanouptime() at process start (meaning time elapsed since system boot) - the resulting timestamp, which we are parsing here, should be UTC based then
                user_time = time_conversion(convert_comp_t(user_time))
                system_time = time_conversion(convert_comp_t(system_time))
                elapsed_time = time_conversion(convert_comp_t(elapsed_time))
                count_io_blocks = convert_comp_t(count_io_blocks)
                flags = parse_flags(flags)
                # result
                accounting_structs.append({'starting_time':starting_time, 'command_name':command_name, 'pid':process_id, 'uid':user_id, 'gid':group_id, 'tty':controlling_tty, 'user_time':user_time, 'system_time':system_time, 'elapsed_time':elapsed_time, 'average_memory_usage':avg_mem_usage, 'count_io_blocks':count_io_blocks, 'flags':flags})
            return accounting_structs

manager.ParsersManager.RegisterParser(OpenBSDSystemAccountingParser)
