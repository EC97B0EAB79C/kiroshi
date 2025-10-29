import unittest
import json
import os
import datetime
from unittest.mock import patch, mock_open
from PIL import Image, ImageFont, ImageDraw
from pathlib import Path

from src import helper
from src.palette import PALETTE_6_COLORS

class TestHelper(unittest.TestCase):

    def setUp(self):
        # Create a dummy JSON file for testing load_json
        self.test_json_path = "test.json"
        with open(self.test_json_path, "w") as f:
            json.dump({"key": "value"}, f)

        # Create a dummy font file for testing load_font
        self.test_font_path = "test_font.ttf"
        # This is a placeholder, actual font file creation is complex
        # For now, we'll rely on mocking or a default font for testing.

    def tearDown(self):
        # Clean up dummy files
        if os.path.exists(self.test_json_path):
            os.remove(self.test_json_path)
        if os.path.exists(self.test_font_path):
            os.remove(self.test_font_path)

    def test_load_json_success(self):
        data = helper.load_json(self.test_json_path)
        self.assertEqual(data, {"key": "value"})

    def test_load_json_file_not_found(self):
        data = helper.load_json("non_existent_file.json")
        self.assertEqual(data, {})

    def test_load_json_decode_error(self):
        with open(self.test_json_path, "w") as f:
            f.write("invalid json")
        data = helper.load_json(self.test_json_path)
        self.assertEqual(data, {})

    @patch('src.helper.Path')
    def test_get_file_modified_time_success(self, mock_path):
        mock_instance = mock_path.return_value
        mock_instance.stat.return_value.st_mtime = 1678886400  # Example timestamp
        expected_datetime = datetime.datetime.fromtimestamp(1678886400)
        result = helper.get_file_modified_time("dummy_path.txt")
        self.assertEqual(result, expected_datetime)

    @patch('src.helper.Path')
    def test_get_file_modified_time_error(self, mock_path):
        mock_instance = mock_path.return_value
        mock_instance.stat.side_effect = Exception("Test error")
        with self.assertRaisesRegex(RuntimeError, "Error getting modified time"):
            helper.get_file_modified_time("dummy_path.txt")

    @patch('src.helper.ImageFont.truetype')
    @patch('src.helper.ImageFont.load_default')
    def test_load_font_success(self, mock_load_default, mock_truetype):
        mock_truetype.return_value = "mock_font"
        font = helper.load_font(self.test_font_path, 12)
        mock_truetype.assert_called_with(self.test_font_path, 12)
        self.assertEqual(font, "mock_font")

    @patch('src.helper.ImageFont.truetype', side_effect=Exception("Font error"))
    @patch('src.helper.ImageFont.load_default')
    def test_load_font_fallback(self, mock_load_default, mock_truetype):
        mock_load_default.return_value = "default_font"
        font = helper.load_font(self.test_font_path, 12)
        mock_load_default.assert_called_with(size=12)
        self.assertEqual(font, "default_font")

    def test_position_center(self):
        bbox = (0, 0, 10, 10)
        width = 100
        height = 50
        x, y = helper.position(bbox, width, height)
        self.assertEqual(x, 45)
        self.assertEqual(y, 20)

    def test_position_top(self):
        bbox = (0, 0, 10, 10)
        width = 100
        height = 50
        x, y = helper.position(bbox, width, height, location="top")
        self.assertEqual(x, 45)
        self.assertEqual(y, 0)

    def test_position_bottom(self):
        bbox = (0, 0, 10, 10)
        width = 100
        height = 50
        x, y = helper.position(bbox, width, height, location="bottom")
        self.assertEqual(x, 45)
        self.assertEqual(y, 40)

    def test_position_with_spacing(self):
        bbox = (0, 0, 10, 10)
        width = 100
        height = 50
        spacing = 5
        x, y = helper.position(bbox, width, height, spacing=spacing)
        self.assertEqual(x, 45)
        self.assertEqual(y, 20)

    def test_cut_text(self):
        # Mock a font object with a getbbox method
        class MockFont:
            def getbbox(self, text):
                # Simulate font width based on text length
                return (0, 0, len(text) * 5, 10) # Assuming each char is 5px wide

        mock_font = MockFont()
        text = "This is a long text that needs to be cut"
        max_width = 20 * 5 # Max 20 characters

        result = helper.cut_text(text, mock_font, max_width)
        expected = """This is a long text
that needs to be cut"""
        self.assertEqual(result, expected)

    def test_truncate_text(self):
        class MockFont:
            def getbbox(self, text):
                return (0, 0, len(text) * 5, 10)

        mock_font = MockFont()
        text = "This is a very long text"
        max_width = 10 * 5 # Max 10 characters

        result = helper.truncate_text(text, mock_font, max_width)
        expected = "This is..."
        self.assertEqual(result, expected)

        text = "Short"
        max_width = 10 * 5
        result = helper.truncate_text(text, mock_font, max_width)
        expected = "Short"
        self.assertEqual(result, expected)

        text = ""
        max_width = 10 * 5
        result = helper.truncate_text(text, mock_font, max_width)
        expected = ""
        self.assertEqual(result, expected)

    def test_fit_and_crop_picture(self):
        # Create a dummy image
        original_image = Image.new('RGB', (100, 50), color = 'red')
        target_size = (50, 50)
        result_image = helper.fit_and_crop_picture(original_image, target_size)
        self.assertEqual(result_image.size, target_size)

        original_image = Image.new('RGB', (50, 100), color = 'blue')
        target_size = (50, 50)
        result_image = helper.fit_and_crop_picture(original_image, target_size)
        self.assertEqual(result_image.size, target_size)

        original_image = Image.new('RGB', (100, 100), color = 'green')
        target_size = (50, 50)
        result_image = helper.fit_and_crop_picture(original_image, target_size)
        self.assertEqual(result_image.size, target_size)

    def test_quantize_image(self):
        # Create a dummy image
        original_image = Image.new('RGB', (10, 10), color = 'red')
        quantized_image = helper.quantize_image(original_image, "6_COLORS")
        self.assertEqual(quantized_image.mode, "P")
        self.assertIsNotNone(quantized_image.getpalette())

    @patch('src.helper.Image.new')
    @patch('src.helper.ImageDraw.Draw')
    @patch('src.helper.load_font')
    @patch('src.helper.Image.open')
    @patch('src.helper.Image.alpha_composite')
    def test_invalid_image(self, mock_alpha_composite, mock_image_open, mock_load_font, mock_draw, mock_image_new):
        mock_image = Image.new('RGB', (100, 100))
        mock_draw_instance = mock_draw.return_value
        mock_draw_instance.textbbox.return_value = (0, 0, 50, 10) # Mock text size
        mock_load_font.return_value = "mock_font"
        mock_image_open.return_value.convert.return_value = Image.new('RGBA', (10, 10))
        mock_alpha_composite.return_value = Image.new('RGBA', (10, 10))
        mock_image_new.return_value = mock_image

        result_image = helper.invalid_image(mock_image, 100, 100)
        self.assertIsNotNone(result_image)
        mock_draw_instance.text.assert_called_once()

if __name__ == '__main__':
    unittest.main()
