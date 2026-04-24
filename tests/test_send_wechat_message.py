import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / ".cursor" / "skills" / "send-wechat-message" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import send_wechat_message as swm  # noqa: E402


class SendWeChatMessageTests(unittest.TestCase):
    def test_parse_args_accepts_repeated_file_flags(self) -> None:
        args = swm.parse_args(
            ["--who", "文件传输助手", "--file", "a.txt", "--file", "b.png", "--timeout", "20"]
        )
        self.assertEqual(args.who, "文件传输助手")
        self.assertEqual(args.files, ["a.txt", "b.png"])
        self.assertEqual(args.timeout, 20)
        self.assertIsNone(args.message)

    def test_resolve_send_payload_rejects_both_message_and_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sample = Path(tmpdir) / "sample.txt"
            sample.write_text("hello", encoding="utf-8")
            with self.assertRaises(swm.WeChatSendError):
                swm.resolve_send_payload("你好", [str(sample)])

    def test_resolve_send_payload_rejects_empty_payload(self) -> None:
        with self.assertRaises(swm.WeChatSendError):
            swm.resolve_send_payload("", [])

    def test_normalize_file_paths_resolves_relative_and_deduplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            previous_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                sample = Path("sample.txt")
                sample.write_text("hello", encoding="utf-8")
                normalized = swm.normalize_file_paths(["sample.txt", str(sample.resolve())])
            finally:
                os.chdir(previous_cwd)
        self.assertEqual(len(normalized), 1)
        self.assertTrue(Path(normalized[0]).is_absolute())

    def test_collect_file_marker_groups_adds_image_marker(self) -> None:
        groups = swm.collect_file_marker_groups(
            [r"C:\tmp\report.docx", r"C:\tmp\photo.png", r"C:\tmp\music.wav"]
        )
        self.assertEqual(groups[0], ["report.docx"])
        self.assertEqual(groups[1], ["photo.png", "图片"])
        self.assertEqual(groups[2], ["music.wav"])

    def test_raw_item_contains_text_and_message_list_contains_text(self) -> None:
        raw_items = [("mmui::ChatBubbleItemView", "文件\nREADME.md\n2.8K")]
        messages = [("self", "README.md 已发送")]
        self.assertTrue(swm.raw_item_contains_text(raw_items, "README.md"))
        self.assertTrue(swm.message_list_contains_text(messages, "README.md"))


if __name__ == "__main__":
    unittest.main()
