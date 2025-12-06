from __future__ import annotations
from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
import tempfile
import os


class BranchesTests(TestCase):
    """Test the branches read and write functions"""

    @patch('syrinx.branches.isfile')
    @patch('syrinx.branches.open', new_callable=mock_open)
    def test_read_branches_empty(self, mocked_open, isfile):
        """Test reading branches when file doesn't exist"""
        from syrinx.branches import read_branches
        isfile.return_value = False
        
        branches = read_branches('/some/root/dir')
        
        self.assertIsNotNone(branches)
        self.assertEqual(len(branches.inner), 0)

    @patch('syrinx.branches.isfile')
    @patch('syrinx.branches.open', new_callable=mock_open)
    def test_read_branches_with_data(self, mocked_open, isfile):
        """Test reading branches from a file with data"""
        from syrinx.branches import read_branches
        isfile.return_value = True
        mocked_open().read.return_value = """main = 2025-10-13T17:45:00+01:00
feature-branch = 2025-11-20T10:30:00+00:00
dev = 2025-12-01T14:15:30+00:00"""
        
        branches = read_branches('/some/root/dir')
        
        self.assertEqual(len(branches.inner), 3)
        self.assertIn('main', branches.inner)
        self.assertIn('feature-branch', branches.inner)
        self.assertIn('dev', branches.inner)
        # Check that the values are datetime objects with the correct ISO string representation
        self.assertEqual(branches.inner['main'].isoformat(), '2025-10-13T17:45:00+01:00')
        self.assertEqual(branches.inner['feature-branch'].isoformat(), '2025-11-20T10:30:00+00:00')
        self.assertEqual(branches.inner['dev'].isoformat(), '2025-12-01T14:15:30+00:00')

    @patch('syrinx.branches.isfile')
    @patch('syrinx.branches.open', new_callable=mock_open)
    def test_read_branches_ignores_invalid_lines(self, mocked_open, isfile):
        """Test that read_branches ignores lines without = separator"""
        from syrinx.branches import read_branches
        isfile.return_value = True
        mocked_open().read.return_value = """main = 2025-10-13T17:45:00+01:00
# This is a comment without equals
feature-branch = 2025-11-20T10:30:00+00:00
invalid line
dev = 2025-12-01T14:15:30+00:00"""
        
        branches = read_branches('/some/root/dir')
        
        self.assertEqual(len(branches.inner), 3)
        self.assertIn('main', branches.inner)
        self.assertIn('feature-branch', branches.inner)
        self.assertIn('dev', branches.inner)

    @patch('syrinx.branches.open', new_callable=mock_open)
    def test_write_branches_with_datetime_objects(self, mocked_open):
        """Test writing branches with datetime objects"""
        from syrinx.branches import write_branches
        
        branches_dict = {
            'main': datetime(2025, 10, 13, 17, 45, 0),
            'feature-branch': datetime(2025, 11, 20, 10, 30, 0),
            'dev': datetime(2025, 12, 1, 14, 15, 30)
        }
        
        write_branches(branches_dict, '/some/root/dir')
        
        # Get what was written
        handle = mocked_open()
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        
        # Verify all branches are present in the output
        self.assertIn('main = 2025-10-13T17:45:00', written_content)
        self.assertIn('feature-branch = 2025-11-20T10:30:00', written_content)
        self.assertIn('dev = 2025-12-01T14:15:30', written_content)

    def test_read_write_roundtrip(self):
        """Test that write_branches and read_branches are inverses"""
        from syrinx.branches import read_branches, write_branches
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Prepare test data with datetime objects
            original_branches = {
                'main': datetime(2025, 10, 13, 17, 45, 0),
                'feature-branch': datetime(2025, 11, 20, 10, 30, 0),
                'dev': datetime(2025, 12, 1, 14, 15, 30)
            }
            
            # Write branches to file
            write_branches(original_branches, tmpdir)
            
            # Read them back
            branches_obj = read_branches(tmpdir)
            
            # Verify the data matches (datetime objects should be equal)
            self.assertEqual(len(branches_obj.inner), 3)
            for branch_name, dt in original_branches.items():
                self.assertIn(branch_name, branches_obj.inner)
                self.assertEqual(branches_obj.inner[branch_name], dt)

    def test_read_write_roundtrip_with_timezone(self):
        """Test roundtrip when writing datetime objects with timezone info"""
        from syrinx.branches import read_branches, write_branches
        from datetime import timezone, timedelta
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Prepare test data with datetime objects including timezone
            tz_plus_one = timezone(timedelta(hours=1))
            tz_utc = timezone.utc
            original_branches = {
                'main': datetime(2025, 10, 13, 17, 45, 0, tzinfo=tz_plus_one),
                'feature-branch': datetime(2025, 11, 20, 10, 30, 0, tzinfo=tz_utc)
            }
            
            # Write branches to file
            write_branches(original_branches, tmpdir)
            
            # Read them back
            branches_obj = read_branches(tmpdir)
            
            # Verify the data matches (datetime objects with timezone should be equal)
            self.assertEqual(len(branches_obj.inner), 2)
            self.assertIn('main', branches_obj.inner)
            self.assertIn('feature-branch', branches_obj.inner)
            self.assertEqual(branches_obj.inner['main'], original_branches['main'])
            self.assertEqual(branches_obj.inner['feature-branch'], original_branches['feature-branch'])
