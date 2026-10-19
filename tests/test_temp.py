import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "temp"


def run_temp(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


class TempTestCase(unittest.TestCase):
    def assert_ok(self, args, expected):
        result = run_temp(args)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stdout, expected + "\n")
        self.assertEqual(result.stderr, "")

    def assert_error(self, args, message=None):
        result = run_temp(args)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        if message is not None:
            self.assertIn(message, result.stderr)
        return result


class ConversionTests(TempTestCase):
    def test_celsius_to_fahrenheit_anchors(self):
        cases = [
            ("0", "32 F"),
            ("100", "212 F"),
            ("-40", "-40 F"),
            ("37", "98.6 F"),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assert_ok(["c2f", value], expected)

    def test_fahrenheit_to_celsius_anchors(self):
        cases = [
            ("32", "0 C"),
            ("212", "100 C"),
            ("-40", "-40 C"),
            ("98.6", "37 C"),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assert_ok(["f2c", value], expected)

    def test_negative_positional_value_is_accepted(self):
        self.assert_ok(["c2f", "-40"], "-40 F")


class FormattingTests(TempTestCase):
    def test_integer_result_has_no_decimal_point(self):
        self.assert_ok(["c2f", "100"], "212 F")

    def test_repeating_decimal_is_limited_to_four_places(self):
        self.assert_ok(["f2c", "1"], "-17.2222 C")

    def test_negative_zero_is_normalized(self):
        self.assert_ok(["f2c", "31.99999999999999"], "0 C")

    def test_trailing_zeros_are_removed(self):
        self.assert_ok(["c2f", "0.5"], "32.9 F")


class PrecisionTests(TempTestCase):
    def test_precision_overrides_default(self):
        self.assert_ok(["f2c", "--precision", "2", "1"], "-17.22 C")

    def test_precision_zero_rounds_to_integer(self):
        self.assert_ok(["c2f", "--precision", "0", "37"], "99 F")

    def test_precision_two_on_integer_trims_trailing_zeros(self):
        self.assert_ok(["c2f", "--precision", "2", "100"], "212 F")

    def test_precision_above_range_is_rejected(self):
        self.assert_error(["c2f", "--precision", "11", "100"])

    def test_precision_below_range_is_rejected(self):
        self.assert_error(["c2f", "--precision", "-1", "100"])

    def test_non_integer_precision_is_rejected(self):
        self.assert_error(["c2f", "--precision", "abc", "100"])


class ValidationTests(TempTestCase):
    def test_non_numeric_is_rejected(self):
        self.assert_error(["c2f", "abc"], "数值无效")

    def test_nan_is_rejected(self):
        self.assert_error(["c2f", "nan"], "数值无效")

    def test_inf_is_rejected(self):
        self.assert_error(["f2c", "inf"], "数值无效")

    def test_below_celsius_absolute_zero_is_rejected(self):
        self.assert_error(["c2f", "-300"], "绝对零度")

    def test_below_fahrenheit_absolute_zero_is_rejected(self):
        self.assert_error(["f2c", "-500"], "绝对零度")

    def test_exact_celsius_absolute_zero_is_accepted(self):
        self.assert_ok(["c2f", "-273.15"], "-459.67 F")

    def test_exact_fahrenheit_absolute_zero_is_accepted(self):
        self.assert_ok(["f2c", "-459.67"], "-273.15 C")

    def test_result_overflow_is_rejected(self):
        self.assert_error(["c2f", "1e308"], "结果超出可表示范围")


class CliShapeTests(TempTestCase):
    def test_no_subcommand_prints_help(self):
        result = run_temp([])
        self.assertEqual(result.returncode, 0)
        self.assertIn("c2f", result.stdout)
        self.assertIn("f2c", result.stdout)

    def test_help_exits_zero(self):
        result = run_temp(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("c2f", result.stdout)

    def test_missing_value_fails(self):
        self.assert_error(["c2f"])

    def test_unknown_subcommand_fails(self):
        self.assert_error(["ftoc", "100"])


if __name__ == "__main__":
    unittest.main()
