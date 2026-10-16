"""
Unit tests for _detect_native_script(). Pure Unicode-range logic, no network
calls and no API key required — safe to run in CI or offline.

    python -m unittest ai_service.tests.test_script_detection
"""
import unittest

from ai_service.service import _detect_native_script


class TestDetectNativeScript(unittest.TestCase):
    def test_devanagari(self):
        self.assertEqual(_detect_native_script("सड़क पर गड्ढा है"), "devanagari")

    def test_kannada(self):
        self.assertEqual(_detect_native_script("ರಸ್ತೆಯಲ್ಲಿ ಗುಂಡಿ ಇದೆ"), "kannada")

    def test_tamil(self):
        self.assertEqual(_detect_native_script("சாலையில் குழி உள்ளது"), "tamil")

    def test_telugu(self):
        self.assertEqual(_detect_native_script("రోడ్డులో గుంతలు ఉన్నాయి"), "telugu")

    def test_english_returns_none(self):
        self.assertIsNone(_detect_native_script("There is a pothole on the road."))

    def test_hinglish_returns_none(self):
        self.assertIsNone(_detect_native_script("Sadak mein gaddha hai, please theek karo."))

    def test_empty_string_returns_none(self):
        self.assertIsNone(_detect_native_script(""))

    def test_mixed_latin_and_devanagari_returns_devanagari(self):
        self.assertEqual(_detect_native_script("The road has गड्ढा here"), "devanagari")


if __name__ == "__main__":
    unittest.main()
