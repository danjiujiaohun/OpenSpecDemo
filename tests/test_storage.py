import json
import tempfile
import unittest

from helpers import data_file, read_data, run_todo, write_data


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_home = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_first_run_creates_data_file_under_xdg_data_home(self):
        result = run_todo(["list"], self.data_home)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(data_file(self.data_home).exists())
        self.assertEqual(read_data(self.data_home), {"version": 1, "next_id": 1, "items": []})
        self.assertIn("0 条未完成", result.stdout)

    def test_data_survives_across_commands(self):
        self.assertEqual(run_todo(["add", "写周报"], self.data_home).returncode, 0)
        result = run_todo(["list"], self.data_home)

        self.assertIn("写周报", result.stdout)
        self.assertEqual(read_data(self.data_home)["items"][0]["text"], "写周报")

    def test_corrupt_json_is_reported_and_not_overwritten(self):
        path = data_file(self.data_home)
        path.parent.mkdir(parents=True)
        path.write_text("{not json", encoding="utf-8")

        result = run_todo(["list"], self.data_home)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("不是合法 JSON", result.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), "{not json")

    def test_invalid_structure_is_reported_and_not_overwritten(self):
        original = json.dumps({"version": 1, "next_id": "x", "items": []})
        path = data_file(self.data_home)
        path.parent.mkdir(parents=True)
        path.write_text(original, encoding="utf-8")

        result = run_todo(["list"], self.data_home)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("格式无效", result.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_atomic_save_leaves_no_temp_file(self):
        run_todo(["add", "一"], self.data_home)
        run_todo(["add", "二"], self.data_home)

        leftovers = [p.name for p in data_file(self.data_home).parent.iterdir() if p.name != "todos.json"]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
