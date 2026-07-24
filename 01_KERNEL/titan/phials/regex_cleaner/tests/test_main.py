import unittest
import importlib.util
import os
import sys

# Since 01_KERNEL starts with a number, we use importlib.util to load the module
MODULE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "main.py"
)
spec = importlib.util.spec_from_file_location("regex_cleaner_main", MODULE_PATH)
regex_cleaner_main = importlib.util.module_from_spec(spec)
sys.modules["regex_cleaner_main"] = regex_cleaner_main
spec.loader.exec_module(regex_cleaner_main)

clean_json = regex_cleaner_main.clean_json


class TestRegexCleaner(unittest.TestCase):
    def test_clean_json_markdown_block(self):
        """Test extraction from standard markdown json block."""
        text = "```json\n{\"key\": \"value\"}\n```"
        result = clean_json(text)
        self.assertEqual(result, '{"key": "value"}')

    def test_clean_json_raw_json(self):
        """Test extraction of raw JSON object without markdown formatting."""
        text = '{"name": "test", "val": 123}'
        result = clean_json(text)
        self.assertEqual(result, '{"name": "test", "val": 123}')

    def test_clean_json_no_json(self):
        """Test fallback case where there is no valid JSON."""
        text = "This is just some random text without any JSON."
        result = clean_json(text)
        self.assertEqual(result, '{}')

    def test_clean_json_extraneous_text(self):
        """Test extraction when there is text before or after the JSON block."""
        text = "Here is the json you requested:\n```json\n{\"data\": [1, 2, 3]}\n```\nHope this helps!"
        result = clean_json(text)
        self.assertEqual(result, '{"data": [1, 2, 3]}')

    def test_clean_json_extraneous_text_raw(self):
        """Test extraction of raw json when there is text before or after."""
        text = "Response:\n{\"status\": \"ok\"}\nEnd of response."
        result = clean_json(text)
        self.assertEqual(result, '{"status": "ok"}')

    def test_clean_json_multiple_json_blocks(self):
        """Test extraction with multiple json blocks (should return the first one matched)."""
        text = "```json\n{\"first\": 1}\n```\n```json\n{\"second\": 2}\n```"
        result = clean_json(text)
        self.assertEqual(result, '{"first": 1}')


if __name__ == "__main__":
    unittest.main()
