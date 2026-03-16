import importlib.util
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "main.py"
CRON_PATH = ROOT / "deploy" / "cron" / "ainformer.cron"
RUN_SCRIPT_PATH = ROOT / "scripts" / "run_inform_group.sh"


def load_main_module():
    spec = importlib.util.spec_from_file_location("ainformer_main", MAIN_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ScheduleGroupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main = load_main_module()

    def test_task_groups_match_expected_sources(self) -> None:
        morning = [task.module for task in self.main._build_tasks("morning", "daily")]
        noon = [task.module for task in self.main._build_tasks("noon", "daily")]
        evening = [task.module for task in self.main._build_tasks("evening", "daily")]

        self.assertEqual(
            morning,
            [
                "core.services.news_hacker_inform",
                "core.services.rundown_ai_inform",
            ],
        )
        self.assertEqual(
            noon,
            [
                "core.services.kr36_inform",
                "core.services.huxiu_inform",
                "core.services.reddit_inform",
            ],
        )
        self.assertEqual(
            evening,
            [
                "core.services.github_trend_inform",
                "core.services.product_hunt_inform",
                "core.services.taaft_inform",
            ],
        )

    def test_all_group_preserves_time_slice_order(self) -> None:
        modules = [task.module for task in self.main._build_tasks("all", "daily")]
        self.assertEqual(
            modules,
            [
                "core.services.news_hacker_inform",
                "core.services.rundown_ai_inform",
                "core.services.kr36_inform",
                "core.services.huxiu_inform",
                "core.services.reddit_inform",
                "core.services.github_trend_inform",
                "core.services.product_hunt_inform",
                "core.services.taaft_inform",
            ],
        )

    def test_cron_file_has_expected_schedule(self) -> None:
        cron_text = CRON_PATH.read_text()
        self.assertIn("0 8 * * * /home/ubuntu/codes/AInformer/scripts/run_inform_group.sh morning", cron_text)
        self.assertIn("0 12 * * * /home/ubuntu/codes/AInformer/scripts/run_inform_group.sh noon", cron_text)
        self.assertIn("0 18 * * * /home/ubuntu/codes/AInformer/scripts/run_inform_group.sh evening", cron_text)

    def test_run_script_rejects_missing_group(self) -> None:
        completed = subprocess.run(
            [str(RUN_SCRIPT_PATH)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Usage:", completed.stderr)


if __name__ == "__main__":
    unittest.main()
