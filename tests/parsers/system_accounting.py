#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the OpenBSD system accounting parser."""

import unittest

from plaso.lib import definitions
from plaso.parsers import system_accounting

from tests.parsers import test_lib


class OpenBSDSystemAccountingParserTest(test_lib.ParserTestCase):
  """Tests for the OpenBSD system accounting parser."""

  def testParseFile(self):
    """Tests the Parse function on a system accounting file from an OpenBSD system."""
    parser = system_accounting.OpenBSDSystemAccountingParser()
    storage_writer = self._ParseFile(['acct'], parser)
    
    # general checks
    number_of_event_data = storage_writer.GetNumberOfAttributeContainers(
        'event_data')
    self.assertEqual(number_of_event_data, 2)
    number_of_warnings = storage_writer.GetNumberOfAttributeContainers(
        'extraction_warning')
    self.assertEqual(number_of_warnings, 0)
    number_of_warnings = storage_writer.GetNumberOfAttributeContainers(
        'recovery_warning')
    self.assertEqual(number_of_warnings, 0)
    
    # content check
    expected_event_values = {
        'data_type': 'openbsd:system_accounting:struct',
        'command_name': 'ls',
        'user_time': '00:00:00.00', 
        'system_time': '00:00:00.00', 
        'elapsed_time': '00:00:00.00', 
        'count_io_blocks': 0.0, 
        'starting_time': '2024-04-22T05:18:06Z',
        'uid': 0, 
        'gid': 0, 
        'average_memory_usage': 0, 
        'tty': 3072, 
        'pid': 66336, 
        'flags': ''}
    event_data = storage_writer.GetAttributeContainerByIndex('event_data', 1)
    self.CheckEventData(event_data, expected_event_values)

if __name__ == '__main__':
  unittest.main()
