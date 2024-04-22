# -*- coding: utf-8 -*-
"""Parser system accounting files on OpenBSD."""

from plaso.parsers import interface
from plaso.parsers import manager

class OpenBSDSystemAccountingParser(interface.FileObjectParser):
  """Parser for system accounting files created on OpenBSD."""

  NAME = "openbsd_system_accounting"
  DATA_FORMAT = "system accounting file"

  def ParseFileObject(self, parser_mediator, file_object):
    """ Parser for system accounting file created by OpenBSD.
    
    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfVFS.
      file_object (dfvfs.FileIO): a file-like object to parse.

    Raises:
      WrongParser: when the file cannot be parsed.
    """
    
    # TODO: logic!

manager.ParsersManager.RegisterParser(OpenBSDSystemAccountingParser)
