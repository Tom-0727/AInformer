from __future__ import annotations

import argparse
import gc
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_GROUP = "all"


@dataclass(frozen=True, slots=True)
class InformTask:
    name: str
    module: str
    args: tuple[str, ...] = ()


def _build_task_map(github_since: str) -> dict[str, InformTask]:
    return {
        "github_trend_inform": InformTask(
            name=f"github_trend_inform({github_since})",
            module="core.services.github_trend_inform",
            args=("--since", github_since),
        ),
        "news_hacker_inform": InformTask(
            name="news_hacker_inform",
            module="core.services.news_hacker_inform",
        ),
        "reddit_inform": InformTask(name="reddit_inform", module="core.services.reddit_inform"),
        "huxiu_inform": InformTask(name="huxiu_inform", module="core.services.huxiu_inform"),
        "kr36_inform": InformTask(name="kr36_inform", module="core.services.kr36_inform"),
        "product_hunt_inform": InformTask(
            name="product_hunt_inform",
            module="core.services.product_hunt_inform",
        ),
        "rundown_ai_inform": InformTask(
            name="rundown_ai_inform",
            module="core.services.rundown_ai_inform",
        ),
        "taaft_inform": InformTask(name="taaft_inform", module="core.services.taaft_inform"),
    }


def _build_tasks(group: str, github_since: str, task_name: str | None = None) -> list[InformTask]:
    task_map = _build_task_map(github_since)
    task_groups = {
        "morning": (
            "news_hacker_inform",
            "rundown_ai_inform",
        ),
        "noon": (
            "kr36_inform",
            "huxiu_inform",
            "reddit_inform",
        ),
        "evening": (
            "github_trend_inform",
            "product_hunt_inform",
            "taaft_inform",
        ),
    }

    if task_name is not None:
        return [task_map[task_name]]

    if group == DEFAULT_GROUP:
        ordered_names = (
            *task_groups["morning"],
            *task_groups["noon"],
            *task_groups["evening"],
        )
    else:
        ordered_names = task_groups[group]

    return [task_map[name] for name in ordered_names]


def _run_task(task: InformTask) -> int:
    cmd = [sys.executable, "-m", task.module, *task.args]
    print(f"\n>>> Running: {task.name}")
    started = time.monotonic()
    completed = subprocess.run(
        cmd,
        cwd=ROOT_DIR,
        check=False,
    )
    elapsed = time.monotonic() - started

    if completed.returncode == 0:
        print(f"<<< Done: {task.name} ({elapsed:.1f}s)")
    else:
        print(f"<<< Failed: {task.name} ({elapsed:.1f}s, exit={completed.returncode})")
    return completed.returncode


def main() -> None:
    task_choices = tuple(_build_task_map("daily").keys())
    parser = argparse.ArgumentParser(
        description=(
            "依次执行 core/services 下指定分组的 inform 任务。"
            "为降低内存峰值，每个任务在独立子进程中运行并在结束后释放内存。"
        )
    )
    selection_group = parser.add_mutually_exclusive_group()
    selection_group.add_argument(
        "--group",
        choices=[DEFAULT_GROUP, "morning", "noon", "evening"],
        help="任务分组。all 表示执行全部分组，默认: all",
    )
    selection_group.add_argument(
        "--task",
        choices=task_choices,
        help="单独执行一个指定信源任务，例如: reddit_inform",
    )
    parser.add_argument(
        "--github-since",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="GitHub Trending 的时间范围（默认: daily）",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="任一任务失败后立即停止后续任务",
    )
    args = parser.parse_args()

    selected_group = args.group or DEFAULT_GROUP
    tasks = _build_tasks(selected_group, args.github_since, args.task)
    failed: list[str] = []

    if args.task:
        print(f"Selected task: {args.task}")
    else:
        print(f"Selected group: {selected_group}")

    for task in tasks:
        returncode = _run_task(task)
        gc.collect()

        if returncode != 0:
            failed.append(task.name)
            if args.fail_fast:
                break

    if failed:
        print("\nRun finished with failures:")
        for idx, name in enumerate(failed, 1):
            print(f"{idx}. {name}")
        raise SystemExit(1)

    print("\nAll inform tasks completed successfully.")


if __name__ == "__main__":
    main()
