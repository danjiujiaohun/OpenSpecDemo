import tempfile
import unittest

from helpers import data_file, read_data, run_todo, write_data


def sample_data():
    return {
        "version": 1,
        "next_id": 5,
        "items": [
            {
                "id": 1,
                "text": "昨天完成的事",
                "created_at": "2026-10-18T08:00:00",
                "completed_at": "2026-10-18T11:20:00",
            },
            {
                "id": 2,
                "text": "昨天没做完的事",
                "created_at": "2026-10-18T09:00:00",
                "completed_at": None,
            },
            {
                "id": 3,
                "text": "今天要做的事",
                "created_at": "2026-10-19T09:12:00",
                "completed_at": None,
            },
            {
                "id": 4,
                "text": "今天已完成的事",
                "created_at": "2026-10-19T10:00:00",
                "completed_at": "2026-10-19T10:30:00",
            },
        ],
    }


class AddTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_home = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_assigns_increasing_ids(self):
        first = run_todo(["add", "写周报"], self.data_home)
        second = run_todo(["add", "买菜"], self.data_home)

        self.assertIn("#1", first.stdout)
        self.assertIn("#2", second.stdout)
        items = read_data(self.data_home)["items"]
        self.assertEqual([item["id"] for item in items], [1, 2])
        self.assertEqual(items[0]["completed_at"], None)
        self.assertRegex(items[0]["created_at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

    def test_blank_text_is_rejected_without_creating_item(self):
        result = run_todo(["add", "   "], self.data_home)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("不能为空", result.stderr)
        self.assertFalse(data_file(self.data_home).exists())


class ListTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_home = self.tmp.name
        write_data(self.data_home, sample_data())

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_only_shows_pending_grouped_by_date_newest_first(self):
        result = run_todo(["list"], self.data_home)
        stdout = result.stdout

        self.assertNotIn("昨天完成的事", stdout)
        self.assertNotIn("今天已完成的事", stdout)
        self.assertIn("昨天没做完的事", stdout)
        self.assertIn("今天要做的事", stdout)
        self.assertLess(stdout.index("2026-10-19"), stdout.index("2026-10-18"))
        self.assertIn("2 条未完成", stdout)

    def test_empty_pending_list_reports_zero(self):
        write_data(self.data_home, {"version": 1, "next_id": 1, "items": []})
        result = run_todo(["list"], self.data_home)

        self.assertEqual(result.returncode, 0)
        self.assertIn("0 条未完成", result.stdout)


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_home = self.tmp.name
        write_data(self.data_home, sample_data())

    def tearDown(self):
        self.tmp.cleanup()

    def test_done_sets_completion_and_removes_from_list(self):
        result = run_todo(["done", "3"], self.data_home)
        item = next(i for i in read_data(self.data_home)["items"] if i["id"] == 3)

        self.assertEqual(result.returncode, 0)
        self.assertIsNotNone(item["completed_at"])
        self.assertNotIn("今天要做的事", run_todo(["list"], self.data_home).stdout)

    def test_done_twice_keeps_original_completion_time(self):
        original = next(i for i in read_data(self.data_home)["items"] if i["id"] == 4)["completed_at"]
        result = run_todo(["done", "4"], self.data_home)
        item = next(i for i in read_data(self.data_home)["items"] if i["id"] == 4)

        self.assertEqual(result.returncode, 0)
        self.assertIn("已完成", result.stdout)
        self.assertEqual(item["completed_at"], original)

    def test_undone_clears_completion(self):
        result = run_todo(["undone", "4"], self.data_home)
        item = next(i for i in read_data(self.data_home)["items"] if i["id"] == 4)

        self.assertEqual(result.returncode, 0)
        self.assertIsNone(item["completed_at"])
        self.assertIn("今天已完成的事", run_todo(["list"], self.data_home).stdout)

    def test_missing_id_errors_without_modifying_data(self):
        before = read_data(self.data_home)
        for command in ("done", "undone", "rm"):
            result = run_todo([command, "999"], self.data_home)
            self.assertNotEqual(result.returncode, 0, command)
            self.assertIn("找不到", result.stderr, command)
        self.assertEqual(read_data(self.data_home), before)

    def test_non_integer_id_is_rejected(self):
        result = run_todo(["done", "abc"], self.data_home)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("id 必须是整数", result.stderr)


class RemoveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_home = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_rm_removes_item_and_ids_are_not_reused(self):
        run_todo(["add", "一"], self.data_home)
        removed = run_todo(["rm", "1"], self.data_home)
        added = run_todo(["add", "二"], self.data_home)

        self.assertEqual(removed.returncode, 0)
        self.assertIn("#2", added.stdout)
        self.assertEqual([i["id"] for i in read_data(self.data_home)["items"]], [2])


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_home = self.tmp.name
        write_data(self.data_home, sample_data())

    def tearDown(self):
        self.tmp.cleanup()

    def test_history_shows_all_items_with_completion_times(self):
        result = run_todo(["history"], self.data_home)
        stdout = result.stdout

        self.assertEqual(result.returncode, 0)
        self.assertIn("昨天完成的事", stdout)
        self.assertIn("昨天没做完的事", stdout)
        self.assertIn("今天要做的事", stdout)
        self.assertIn("-> 11:20", stdout)
        self.assertIn("共 4 条记录", stdout)
        self.assertLess(stdout.index("2026-10-19"), stdout.index("2026-10-18"))

    def test_history_date_filters_by_creation_date(self):
        result = run_todo(["history", "--date", "2026-10-18"], self.data_home)
        stdout = result.stdout

        self.assertEqual(result.returncode, 0)
        self.assertIn("昨天完成的事", stdout)
        self.assertIn("昨天没做完的事", stdout)
        self.assertNotIn("今天要做的事", stdout)
        self.assertIn("共 2 条记录", stdout)

    def test_history_invalid_date_is_rejected(self):
        result = run_todo(["history", "--date", "not-a-date"], self.data_home)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("日期格式应为 YYYY-MM-DD", result.stderr)


if __name__ == "__main__":
    unittest.main()
