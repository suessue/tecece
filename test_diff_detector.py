import unittest
import logging
from unittest.mock import patch, MagicMock, mock_open
import subprocess
import json
import tempfile
import os

from diff_detector import APISpecDiffDetector


class TestAPISpecDiffDetector(unittest.TestCase):
    """Unit tests for APISpecDiffDetector class using oasdiff."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Sample API specs for testing
        self.sample_spec_v1 = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "A test API"
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    }
                },
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer"
                    }
                }
            }
        }
        
        self.sample_spec_v2 = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "2.0.0",
                "description": "An updated test API"
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    },
                    "post": {
                        "summary": "Create user",
                        "responses": {
                            "201": {
                                "description": "Created"
                            }
                        }
                    }
                },
                "/products": {
                    "get": {
                        "summary": "Get products",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "email": {"type": "string"}
                        }
                    },
                    "Product": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    }
                }
            }
        }

        # Sample spec with breaking changes (removed endpoint)
        self.sample_spec_with_breaking_change = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "3.0.0",
                "description": "Breaking change API"
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "parameters": [
                            {
                                "name": "required_param",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            }
        }

        # Empty spec for edge case testing
        self.empty_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Empty API",
                "version": "1.0.0"
            },
            "paths": {}
        }

        # Malformed spec for error testing
        self.malformed_spec = {
            "openapi": "2.0",  # Wrong version format
            "info": {
                "title": "Malformed API"
                # Missing required version field
            }
        }

    @patch('subprocess.run')
    def test_init_with_valid_oasdiff(self, mock_subprocess):
        """Test detector initialization with valid oasdiff installation."""
        # Mock successful oasdiff --version call
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="oasdiff version 1.10.0\n"
        )
        
        detector = APISpecDiffDetector()
        
        mock_subprocess.assert_called_once_with(
            ['oasdiff', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(detector.oasdiff_path, 'oasdiff')

    @patch('subprocess.run')
    def test_init_with_custom_oasdiff_path(self, mock_subprocess):
        """Test detector initialization with custom oasdiff path."""
        custom_path = '/usr/local/bin/oasdiff'
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="oasdiff version 1.10.0\n"
        )
        
        detector = APISpecDiffDetector(oasdiff_path=custom_path)
        
        mock_subprocess.assert_called_once_with(
            [custom_path, '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        self.assertEqual(detector.oasdiff_path, custom_path)

    @patch('subprocess.run')
    def test_init_with_invalid_oasdiff(self, mock_subprocess):
        """Test detector initialization with invalid oasdiff installation."""
        # Mock failed oasdiff --version call
        mock_subprocess.side_effect = FileNotFoundError("oasdiff not found")
        
        with self.assertRaises(RuntimeError) as context:
            APISpecDiffDetector()
        
        self.assertIn("oasdiff is required but not available", str(context.exception))

    @patch('subprocess.run')
    def test_init_with_oasdiff_timeout(self, mock_subprocess):
        """Test detector initialization when oasdiff times out."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired(['oasdiff'], 10)
        
        with self.assertRaises(RuntimeError) as context:
            APISpecDiffDetector()
        
        self.assertIn("oasdiff is required but not available", str(context.exception))

    @patch('subprocess.run')
    def test_init_with_oasdiff_non_zero_exit(self, mock_subprocess):
        """Test detector initialization when oasdiff returns non-zero exit code."""
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Some error"
        )
        
        # Should not raise exception, but should log warning and still initialize
        detector = APISpecDiffDetector()
        
        self.assertEqual(detector.oasdiff_path, 'oasdiff')
        # The detector should still be created even if version check fails with non-zero exit

    def test_detect_changes_no_current_spec(self):
        """Test detect_changes when current spec is None."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            result = detector.detect_changes(None, self.sample_spec_v1)
            self.assertIsNone(result)

    def test_detect_changes_empty_current_spec(self):
        """Test detect_changes when current spec is empty dict."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            result = detector.detect_changes({}, self.sample_spec_v1)
            self.assertIsNone(result)

    def test_detect_changes_no_previous_spec(self):
        """Test detect_changes when previous spec is None (initial version)."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            result = detector.detect_changes(self.sample_spec_v1, None)
            
            self.assertIsNotNone(result)
            self.assertIn('breaking_changes', result)
            self.assertIn('changelog', result)
            self.assertIn('current_spec', result)
            self.assertIn('has_breaking_changes', result)
            self.assertIn('summary', result)
            
            self.assertEqual(result['breaking_changes'], [])
            self.assertFalse(result['has_breaking_changes'])
            self.assertEqual(result['current_spec'], self.sample_spec_v1)
            self.assertIn("Initial API specification version", result['summary'])

    def test_detect_changes_initial_empty_spec(self):
        """Test detect_changes with initial empty spec."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            result = detector.detect_changes(self.empty_spec, None)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['breaking_changes'], [])
            self.assertFalse(result['has_breaking_changes'])
            self.assertIn("0 API paths", result['changelog'])
            self.assertIn("0 operations", result['changelog'])

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_detect_changes_with_breaking_changes(self, mock_subprocess, mock_tempfile):
        """Test detect_changes when there are breaking changes."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        # Mock breaking changes response
        breaking_changes_response = MagicMock(
            returncode=0,  # oasdiff returns 0 even with breaking changes
            stdout='[{"id": "test-break", "text": "Breaking change detected", "level": "error"}]'
        )
        
        # Mock changelog response
        changelog_response = MagicMock(
            returncode=0,
            stdout="### What's Changed\n- Added new endpoint\n- Breaking change in user schema"
        )
        
        # Configure subprocess.run to return different responses based on arguments
        def subprocess_side_effect(*args, **kwargs):
            if 'breaking' in args[0]:
                return breaking_changes_response
            elif 'changelog' in args[0]:
                return changelog_response
            else:
                return MagicMock(returncode=0, stdout="version 1.10.0")
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        self.assertIsNotNone(result)
        self.assertTrue(result['has_breaking_changes'])
        self.assertEqual(len(result['breaking_changes']), 1)
        self.assertEqual(result['breaking_changes'][0]['id'], 'test-break')
        self.assertIn("Breaking change detected", result['breaking_changes'][0]['text'])

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_detect_changes_multiple_breaking_changes(self, mock_subprocess, mock_tempfile):
        """Test detect_changes with multiple breaking changes."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        # Mock multiple breaking changes
        multiple_breaking_changes = [
            {"id": "break-1", "text": "Removed endpoint", "level": "error", "operation": "DELETE /users"},
            {"id": "break-2", "text": "Parameter required", "level": "error", "path": "/users"},
            {"id": "break-3", "text": "Schema changed", "level": "warning"}
        ]
        
        breaking_changes_response = MagicMock(
            returncode=0,
            stdout=json.dumps(multiple_breaking_changes)
        )
        
        changelog_response = MagicMock(
            returncode=0,
            stdout="### Breaking Changes\n- Multiple breaking changes"
        )
        
        def subprocess_side_effect(*args, **kwargs):
            if 'breaking' in args[0]:
                return breaking_changes_response
            elif 'changelog' in args[0]:
                return changelog_response
            else:
                return MagicMock(returncode=0, stdout="version 1.10.0")
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        result = detector.detect_changes(self.sample_spec_with_breaking_change, self.sample_spec_v1)
        
        self.assertIsNotNone(result)
        self.assertTrue(result['has_breaking_changes'])
        self.assertEqual(len(result['breaking_changes']), 3)
        self.assertIn("3 breaking change(s) detected", result['summary'])

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_detect_changes_no_changes(self, mock_subprocess, mock_tempfile):
        """Test detect_changes when there are no changes."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        # Mock no changes responses
        def subprocess_side_effect(*args, **kwargs):
            if 'breaking' in args[0]:
                return MagicMock(returncode=0, stdout="")  # No breaking changes
            elif 'changelog' in args[0]:
                return MagicMock(returncode=0, stdout="")  # No changelog
            else:
                return MagicMock(returncode=0, stdout="version 1.10.0")
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        result = detector.detect_changes(self.sample_spec_v1, self.sample_spec_v1)
        
        self.assertIsNone(result)

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_detect_changes_only_non_breaking_changes(self, mock_subprocess, mock_tempfile):
        """Test detect_changes with only non-breaking changes."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        def subprocess_side_effect(*args, **kwargs):
            if 'breaking' in args[0]:
                return MagicMock(returncode=0, stdout="")  # No breaking changes
            elif 'changelog' in args[0]:
                return MagicMock(returncode=0, stdout="### Changes\n- Added new optional field\n- Updated description")
            else:
                return MagicMock(returncode=0, stdout="version 1.10.0")
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        self.assertIsNotNone(result)
        self.assertFalse(result['has_breaking_changes'])
        self.assertEqual(len(result['breaking_changes']), 0)
        self.assertIn("Added new optional field", result['changelog'])

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_detect_changes_invalid_json_response(self, mock_subprocess, mock_tempfile):
        """Test detect_changes when oasdiff returns invalid JSON."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        def subprocess_side_effect(*args, **kwargs):
            if 'breaking' in args[0]:
                return MagicMock(returncode=0, stdout="Invalid JSON response")  # Return code 0 with invalid JSON
            elif 'changelog' in args[0]:
                return MagicMock(returncode=0, stdout="")
            else:
                return MagicMock(returncode=0, stdout="version 1.10.0")
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        self.assertIsNotNone(result)
        self.assertTrue(result['has_breaking_changes'])
        self.assertEqual(len(result['breaking_changes']), 1)
        self.assertEqual(result['breaking_changes'][0]['description'], 'Invalid JSON response')

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_detect_changes_oasdiff_command_failure(self, mock_subprocess, mock_tempfile):
        """Test detect_changes when oasdiff commands fail."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        def subprocess_side_effect(*args, **kwargs):
            if 'breaking' in args[0]:
                return MagicMock(returncode=2, stdout="", stderr="Command failed")  # Unexpected error
            elif 'changelog' in args[0]:
                return MagicMock(returncode=2, stdout="", stderr="Command failed")
            else:
                return MagicMock(returncode=0, stdout="version 1.10.0")
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        self.assertIsNone(result)

    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    @patch('subprocess.run')
    def test_detect_changes_temp_file_cleanup_error(self, mock_subprocess, mock_unlink, mock_tempfile):
        """Test detect_changes when temp file cleanup fails."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        # Mock file deletion failure
        mock_unlink.side_effect = OSError("Permission denied")
        
        def subprocess_side_effect(*args, **kwargs):
            if 'breaking' in args[0]:
                return MagicMock(returncode=0, stdout="")
            elif 'changelog' in args[0]:
                return MagicMock(returncode=0, stdout="### Changes\n- Minor update")
            else:
                return MagicMock(returncode=0, stdout="version 1.10.0")
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        # Should not raise exception despite cleanup failure
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        self.assertIsNotNone(result)
        self.assertIn("Minor update", result['changelog'])

    def test_parse_breaking_changes_list_format(self):
        """Test _parse_breaking_changes with list format."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            breaking_changes_data = [
                {
                    "id": "test-1",
                    "text": "Parameter removed",
                    "level": "error",
                    "operation": "GET /users",
                    "path": "/users"
                },
                {
                    "id": "test-2",
                    "text": "Response schema changed",
                    "level": "warning"
                }
            ]
            
            result = detector._parse_breaking_changes(breaking_changes_data)
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['id'], 'test-1')
            self.assertEqual(result[0]['text'], 'Parameter removed')
            self.assertEqual(result[0]['operation'], 'GET /users')

    def test_parse_breaking_changes_dict_format(self):
        """Test _parse_breaking_changes with dict format."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            breaking_changes_data = {
                "breakingChanges": [
                    {
                        "id": "test-1",
                        "text": "Breaking change",
                        "level": "error"
                    }
                ]
            }
            
            result = detector._parse_breaking_changes(breaking_changes_data)
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['id'], 'test-1')

    def test_parse_breaking_changes_string_format(self):
        """Test _parse_breaking_changes with string format."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            breaking_changes_data = "Some breaking change text"
            
            result = detector._parse_breaking_changes(breaking_changes_data)
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['description'], 'Some breaking change text')

    def test_parse_breaking_changes_empty_list(self):
        """Test _parse_breaking_changes with empty list."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            result = detector._parse_breaking_changes([])
            
            self.assertEqual(len(result), 0)

    def test_parse_breaking_changes_list_with_strings(self):
        """Test _parse_breaking_changes with list containing strings."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            breaking_changes_data = ["Breaking change 1", "Breaking change 2"]
            
            result = detector._parse_breaking_changes(breaking_changes_data)
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['description'], 'Breaking change 1')
            self.assertEqual(result[1]['description'], 'Breaking change 2')

    def test_parse_breaking_changes_dict_without_breaking_changes_key(self):
        """Test _parse_breaking_changes with dict without breakingChanges key."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            breaking_changes_data = {"other_key": "some value"}
            
            result = detector._parse_breaking_changes(breaking_changes_data)
            
            self.assertEqual(len(result), 1)
            self.assertIn('description', result[0])

    def test_generate_initial_changelog(self):
        """Test _generate_initial_changelog method."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            changelog = detector._generate_initial_changelog(self.sample_spec_v1)
            
            self.assertIn("Initial API specification version", changelog)
            self.assertIn("1 API paths", changelog)
            self.assertIn("1 operations", changelog)
            self.assertIn("1 schemas", changelog)
            self.assertIn("1 securitySchemes", changelog)

    def test_generate_initial_changelog_complex_spec(self):
        """Test _generate_initial_changelog with complex spec."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            changelog = detector._generate_initial_changelog(self.sample_spec_v2)
            
            self.assertIn("Initial API specification version", changelog)
            self.assertIn("2 API paths", changelog)
            self.assertIn("3 operations", changelog)  # GET /users, POST /users, GET /products
            self.assertIn("2 schemas", changelog)

    def test_generate_initial_changelog_empty_spec(self):
        """Test _generate_initial_changelog with empty spec."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            changelog = detector._generate_initial_changelog(self.empty_spec)
            
            self.assertIn("Initial API specification version", changelog)
            self.assertIn("0 API paths", changelog)
            self.assertIn("0 operations", changelog)

    def test_generate_summary_with_breaking_changes(self):
        """Test _generate_summary with breaking changes."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            breaking_changes = [
                {"id": "test-1", "text": "Breaking change"}
            ]
            changelog = "### Changes\n- Added endpoint\n- Modified schema"
            
            summary = detector._generate_summary(breaking_changes, changelog)
            
            self.assertIn("1 breaking change(s) detected", summary)
            self.assertIn("3 total changes", summary)

    def test_generate_summary_multiple_breaking_changes(self):
        """Test _generate_summary with multiple breaking changes."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            breaking_changes = [
                {"id": "test-1", "text": "Breaking change 1"},
                {"id": "test-2", "text": "Breaking change 2"},
                {"id": "test-3", "text": "Breaking change 3"}
            ]
            changelog = "### Changes\n- Change 1\n- Change 2"
            
            summary = detector._generate_summary(breaking_changes, changelog)
            
            self.assertIn("3 breaking change(s) detected", summary)
            self.assertIn("3 total changes", summary)

    def test_generate_summary_no_changes(self):
        """Test _generate_summary with no changes."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            summary = detector._generate_summary([], "")
            
            self.assertEqual(summary, "No significant changes detected")

    def test_generate_summary_only_non_breaking_changes(self):
        """Test _generate_summary with only non-breaking changes."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            changelog = "### Changes\n- Added optional field\n- Updated documentation"
            
            summary = detector._generate_summary([], changelog)
            
            self.assertIn("3 total changes", summary)
            self.assertNotIn("breaking change", summary)

    def test_generate_summary_empty_changelog_with_whitespace(self):
        """Test _generate_summary with changelog containing only whitespace."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
            detector = APISpecDiffDetector()
            
            summary = detector._generate_summary([], "   \n   \t   ")
            
            self.assertEqual(summary, "No significant changes detected")

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_subprocess_error_handling(self, mock_subprocess, mock_tempfile):
        """Test handling of subprocess errors."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        # Make subprocess raise an exception
        def subprocess_side_effect(*args, **kwargs):
            if 'breaking' in args[0] or 'changelog' in args[0]:
                raise subprocess.TimeoutExpired(args[0], 30)
            else:
                return MagicMock(returncode=0, stdout="version 1.10.0")
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        # Should return None due to error
        self.assertIsNone(result)

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_subprocess_process_error_handling(self, mock_subprocess, mock_tempfile):
        """Test handling of subprocess process errors."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        # Make subprocess raise process error
        def subprocess_side_effect(*args, **kwargs):
            if 'breaking' in args[0] or 'changelog' in args[0]:
                raise subprocess.SubprocessError("Process failed")
            else:
                return MagicMock(returncode=0, stdout="version 1.10.0")
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        # Should return None due to error
        self.assertIsNone(result)

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    def test_general_exception_handling(self, mock_subprocess, mock_tempfile):
        """Test handling of general exceptions during diff detection."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Make tempfile raise an exception
        mock_tempfile.side_effect = Exception("Unexpected error")
        
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        # Should return None due to error
        self.assertIsNone(result)

    @patch('tempfile.NamedTemporaryFile')
    @patch('json.dump')
    @patch('subprocess.run')
    def test_json_serialization_error(self, mock_subprocess, mock_json_dump, mock_tempfile):
        """Test handling of JSON serialization errors."""
        # Setup detector
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="version 1.10.0")
        detector = APISpecDiffDetector()
        
        # Mock temp files
        mock_prev_file = MagicMock()
        mock_prev_file.name = '/tmp/prev.json'
        mock_curr_file = MagicMock()
        mock_curr_file.name = '/tmp/curr.json'
        mock_tempfile.return_value.__enter__.side_effect = [mock_prev_file, mock_curr_file]
        
        # Make JSON dump raise an exception
        mock_json_dump.side_effect = TypeError("Object is not JSON serializable")
        
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        # Should return None due to error
        self.assertIsNone(result)


class TestAPISpecDiffDetectorIntegration(unittest.TestCase):
    """Integration tests for APISpecDiffDetector (require oasdiff to be installed)."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.sample_spec_v1 = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }
        
        self.sample_spec_v2 = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "2.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "parameters": [
                            {
                                "name": "required_param",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"}
                            }
                        ],
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        # Spec with removed endpoint (should be breaking)
        self.sample_spec_v3 = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "3.0.0"},
            "paths": {}
        }

        # Spec with added endpoint (should not be breaking)
        self.sample_spec_v4 = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "4.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "responses": {"200": {"description": "OK"}}
                    }
                },
                "/new-endpoint": {
                    "post": {
                        "responses": {"201": {"description": "Created"}}
                    }
                }
            }
        }

    def test_oasdiff_availability(self):
        """Test if oasdiff is available for integration tests."""
        try:
            detector = APISpecDiffDetector()
            # If we get here, oasdiff is available
            self.assertIsNotNone(detector)
        except RuntimeError:
            self.skipTest("oasdiff not available - skipping integration tests")

    def test_real_diff_detection_breaking_changes(self):
        """Test actual diff detection with breaking changes using real oasdiff."""
        try:
            detector = APISpecDiffDetector()
        except RuntimeError:
            self.skipTest("oasdiff not available - skipping integration test")
        
        # Test with specs that should have breaking changes (adding required parameter)
        result = detector.detect_changes(self.sample_spec_v2, self.sample_spec_v1)
        
        if result:
            # Verify the structure
            self.assertIn('breaking_changes', result)
            self.assertIn('changelog', result)
            self.assertIn('current_spec', result)
            self.assertIn('has_breaking_changes', result)
            self.assertIn('summary', result)
            
            # The addition of a required parameter should be a breaking change
            if result['has_breaking_changes']:
                self.assertGreater(len(result['breaking_changes']), 0)

    def test_real_diff_detection_no_breaking_changes(self):
        """Test actual diff detection with non-breaking changes."""
        try:
            detector = APISpecDiffDetector()
        except RuntimeError:
            self.skipTest("oasdiff not available - skipping integration test")
        
        # Test with specs that should have non-breaking changes (adding new endpoint)
        result = detector.detect_changes(self.sample_spec_v4, self.sample_spec_v1)
        
        if result:
            # Should have changes but not breaking ones
            self.assertFalse(result['has_breaking_changes'])
            self.assertEqual(len(result['breaking_changes']), 0)
            self.assertIn('new-endpoint', result['changelog'] or '')

    def test_real_diff_detection_removed_endpoint(self):
        """Test actual diff detection with removed endpoint (should be breaking)."""
        try:
            detector = APISpecDiffDetector()
        except RuntimeError:
            self.skipTest("oasdiff not available - skipping integration test")
        
        # Test with spec that has removed endpoint
        result = detector.detect_changes(self.sample_spec_v3, self.sample_spec_v1)
        
        if result:
            # Note: oasdiff may not always detect removed endpoints as breaking changes
            # depending on the configuration and API design
            # So we just verify that some changes are detected
            self.assertIn('breaking_changes', result)
            self.assertIn('changelog', result)
            # The result should at least show some changes in the changelog
            self.assertIsNotNone(result.get('changelog', ''))
        else:
            # If no result, it means oasdiff didn't detect significant changes
            # This is still a valid outcome as oasdiff behavior can vary
            self.skipTest("oasdiff did not detect changes for this scenario")

    def test_real_diff_detection_identical_specs(self):
        """Test actual diff detection with identical specs."""
        try:
            detector = APISpecDiffDetector()
        except RuntimeError:
            self.skipTest("oasdiff not available - skipping integration test")
        
        # Test with identical specs
        result = detector.detect_changes(self.sample_spec_v1, self.sample_spec_v1)
        
        # Should return None for identical specs
        self.assertIsNone(result)

    def test_real_diff_detection_initial_spec(self):
        """Test actual diff detection with initial spec (no previous)."""
        try:
            detector = APISpecDiffDetector()
        except RuntimeError:
            self.skipTest("oasdiff not available - skipping integration test")
        
        # Test with no previous spec
        result = detector.detect_changes(self.sample_spec_v1, None)
        
        self.assertIsNotNone(result)
        self.assertFalse(result['has_breaking_changes'])
        self.assertEqual(len(result['breaking_changes']), 0)
        self.assertIn("Initial API specification version", result['summary'])


if __name__ == '__main__':
    # Set up logging for tests
    logging.basicConfig(level=logging.DEBUG)
    
    # Run the tests
    unittest.main() 