from unittest import TestCase
from unittest.mock import Mock
from datetime import datetime, UTC
from syrinx.node import ContentNode
from syrinx.branches import Branches
from syrinx.exceptions import UnknownBranchError


class ContentNodeLastModifiedTests(TestCase):
    """Tests for ContentNode.lastModified property with branch lookup support"""

    def test_lastModified_direct_entry(self):
        """Test that direct LastModified entry is converted to datetime"""
        config = Mock()
        config.branches = Branches({})
        
        node = ContentNode(config)
        node.front = {'LastModified': '2025-10-01T12:00:00'}
        
        result = node.lastModified
        self.assertIsInstance(result, datetime)
        self.assertEqual(result, datetime(2025, 10, 1, 12, 0, 0))

    def test_lastModified_branch_lookup(self):
        """Test that LastModifiedBranch returns datetime from branch lookup"""
        config = Mock()
        branches_dict = {
            'main': datetime(2025, 12, 6, 13, 15, 24, 42024, tzinfo=UTC),
        }
        config.branches = Branches(branches_dict)
        
        node = ContentNode(config)
        node.front = {'LastModifiedBranch': 'main'}
        
        result = node.lastModified
        self.assertIsInstance(result, datetime)
        self.assertEqual(result, datetime(2025, 12, 6, 13, 15, 24, 42024, tzinfo=UTC))

    def test_lastModified_branch_lookup_different_branch(self):
        """Test branch lookup with multiple branches"""
        config = Mock()
        branches_dict = {
            'main': datetime(2025, 12, 6, 13, 15, 24, tzinfo=UTC),
            'feature-branch': datetime(2025, 11, 15, 10, 30, 0, tzinfo=UTC),
        }
        config.branches = Branches(branches_dict)
        
        node = ContentNode(config)
        node.front = {'LastModifiedBranch': 'feature-branch'}
        
        result = node.lastModified
        self.assertIsInstance(result, datetime)
        self.assertEqual(result, datetime(2025, 11, 15, 10, 30, 0, tzinfo=UTC))

    def test_lastModified_direct_takes_precedence(self):
        """Test that direct LastModified takes precedence over LastModifiedBranch"""
        config = Mock()
        branches_dict = {
            'main': datetime(2025, 12, 6, 13, 15, 24, tzinfo=UTC),
        }
        config.branches = Branches(branches_dict)
        
        node = ContentNode(config)
        node.front = {
            'LastModified': '2025-09-01T08:00:00',
            'LastModifiedBranch': 'main'
        }
        
        result = node.lastModified
        self.assertIsInstance(result, datetime)
        self.assertEqual(result, datetime(2025, 9, 1, 8, 0, 0))

    def test_lastModified_no_entries(self):
        """Test that None is returned when no entries present"""
        config = Mock()
        config.branches = Branches({})
        
        node = ContentNode(config)
        node.front = {}
        
        self.assertIsNone(node.lastModified)

    def test_lastModified_unknown_branch_raises_error(self):
        """Test that UnknownBranchError is raised for unknown branch"""
        config = Mock()
        branches_dict = {
            'main': datetime(2025, 12, 6, 13, 15, 24, tzinfo=UTC),
        }
        config.branches = Branches(branches_dict)
        
        node = ContentNode(config)
        node.front = {'LastModifiedBranch': 'nonexistent-branch'}
        
        with self.assertRaises(UnknownBranchError) as cm:
            _ = node.lastModified
        
        self.assertIn('nonexistent-branch', str(cm.exception))
        self.assertIn('not found', str(cm.exception))
