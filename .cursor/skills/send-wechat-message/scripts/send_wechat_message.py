import argparse
import difflib
import importlib
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, List, Optional, Tuple


class WeChatSendError(RuntimeError):
    pass


def patch_wxauto4_profile_popup(module: Any) -> None:
    """Short-circuit wxauto4 get_my_info to avoid opening profile card."""
    if getattr(module, "__name__", "") not in {"wxauto4", "wxautox4"}:
        return

    try:
        from wxauto4.ui import main as wxauto4_main  # type: ignore
    except Exception:
        return

    wnd_cls = getattr(wxauto4_main, "WeChatMainWnd", None)
    if wnd_cls is None:
        return
    if getattr(wnd_cls, "_safe_get_my_info_patched", False):
        return

    def _safe_get_my_info(self, *args, **kwargs):
        if not getattr(wnd_cls, "_safe_get_my_info_logged", False):
            wnd_cls._safe_get_my_info_logged = True
            print("[wxauto4 compat] short-circuited get_my_info() to avoid profile popup")
        return {"nickname": "", "wxid": "", "alias": ""}

    wnd_cls.get_my_info = _safe_get_my_info
    wnd_cls._safe_get_my_info_patched = True


def ensure_tkinter_stub() -> None:
    """wxauto4 may import tkinter at module import time.

    The packaged runtime and some build runtimes may not include Tk. For our
    send-message workflow, a tiny stub is enough to let wxauto4 import.
    """
    if "tkinter" in sys.modules:
        return

    try:
        import tkinter  # noqa: F401
        return
    except Exception:
        pass

    import types

    tk = types.ModuleType("tkinter")
    tk.END = "end"
    tk.TclError = RuntimeError
    tk.Tk = type("Tk", (), {})
    tk.Toplevel = type("Toplevel", (), {})
    tk.Misc = type("Misc", (), {})

    for submodule_name in ("filedialog", "messagebox", "simpledialog", "ttk"):
        submodule = types.ModuleType(f"tkinter.{submodule_name}")
        setattr(tk, submodule_name, submodule)
        sys.modules[f"tkinter.{submodule_name}"] = submodule

    sys.modules["tkinter"] = tk


def import_wechat_backend() -> Tuple[Any, str]:
    errors: List[str] = []
    ensure_tkinter_stub()
    for module_name, variant_name in (
        ("wxauto4", "wxauto4"),
        ("wxautox4", "wxautox4"),
        ("wxauto", "wxauto"),
    ):
        try:
            module = importlib.import_module(module_name)
            patch_wxauto4_profile_popup(module)
            return module, variant_name
        except Exception as exc:
            errors.append(f"{module_name}: {exc}")

    raise WeChatSendError(
        "未安装可用的微信自动化依赖。\n"
        "可依次尝试以下安装来源：\n"
        "1) pip install wxauto4\n"
        "2) pip install wxautox4\n"
        "3) pip install git+https://github.com/cluic/wxauto4.git\n"
        "如果你明确使用的是微信 3.9.x 旧版，再考虑安装老版 wxauto。\n"
        f"导入详情: {' | '.join(errors)}"
    )


def common_wechat_paths() -> List[Path]:
    program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
    user_profile = Path(os.environ.get("USERPROFILE", ""))

    paths = [
        program_files / "Tencent" / "Weixin" / "Weixin.exe",
        program_files_x86 / "Tencent" / "Weixin" / "Weixin.exe",
        program_files / "Tencent" / "WeChat" / "WeChat.exe",
        program_files_x86 / "Tencent" / "WeChat" / "WeChat.exe",
    ]
    if str(user_profile):
        paths.append(
            user_profile / "AppData" / "Roaming" / "Tencent" / "xwechat" / "Weixin.exe"
        )
    return paths


def launch_wechat() -> Optional[Path]:
    for exe in common_wechat_paths():
        if not exe.exists():
            continue
        try:
            subprocess.Popen([str(exe)], close_fds=True)
            return exe
        except Exception:
            continue
    return None


def attach_wechat(wxauto_module: Any, variant: str, timeout_seconds: int) -> Any:
    launched = False
    last_error: Optional[Exception] = None
    deadline = time.time() + max(3, timeout_seconds)

    while time.time() < deadline:
        try:
            try:
                return wxauto_module.WeChat(ads=False)
            except TypeError:
                return wxauto_module.WeChat()
        except Exception as exc:
            last_error = exc
            if not launched:
                launch_wechat()
                launched = True
            time.sleep(1)

    hint = [
        f"无法连接桌面微信（后端: {variant}）。",
        f"最后一次错误: {last_error}",
        "请确认桌面微信已经登录且窗口可见，不要缩到系统托盘。",
    ]
    if variant in {"wxauto4", "wxautox4"}:
        hint.extend(
            [
                "如果你使用的是微信 4.x，首次使用前通常需要设置 QT_ACCESSIBILITY=1。",
                '可执行: [Environment]::SetEnvironmentVariable("QT_ACCESSIBILITY", "1", "User")',
                "设置后请完全退出微信并重新打开。",
            ]
        )
    raise WeChatSendError("\n".join(hint))


def switch_to_chat_page(wx: Any) -> None:
    try:
        if hasattr(wx, "SwitchToChat"):
            wx.SwitchToChat()
    except Exception:
        pass


def list_sessions(wx: Any, variant: str) -> List[str]:
    switch_to_chat_page(wx)
    if variant == "wxauto4":
        sessions = wx.GetSession() or []
        result = []
        for session in sessions:
            name = getattr(session, "name", None) or getattr(session, "who", None) or ""
            name = str(name).strip()
            if name:
                result.append(name)
        return result

    sessions = wx.GetSessionList(reset=True) or {}
    return [str(name).strip() for name in sessions.keys() if str(name).strip()]


def normalize_name(value: str) -> str:
    return "".join((value or "").strip().lower().split())


def current_chat_name(wx: Any, variant: str) -> str:
    if variant == "wxauto4":
        try:
            info = wx.ChatInfo() or {}
            return str(info.get("chat_name") or info.get("name") or "").strip()
        except Exception:
            return ""
    try:
        return str(wx.CurrentChat() or "").strip()
    except Exception:
        return ""


def wait_current_chat_name(wx: Any, variant: str, timeout_seconds: float = 2.0) -> str:
    deadline = time.time() + max(0.2, timeout_seconds)
    while time.time() < deadline:
        name = current_chat_name(wx, variant)
        if name:
            return name
        time.sleep(0.2)
    return ""


def chat_name_matches(actual: str, expected: str) -> bool:
    actual_name = (actual or "").strip()
    expected_name = (expected or "").strip()
    if not actual_name or not expected_name:
        return False
    return normalize_name(actual_name) == normalize_name(expected_name)


def resolve_target_chat_name(wx: Any, variant: str, who: str) -> str:
    target = (who or "").strip()
    try:
        sessions = list_sessions(wx, variant)
    except Exception as exc:
        print(f"[compat] failed to enumerate sessions, fallback to direct search: {exc}")
        return target
    if not sessions:
        return target

    if target in sessions:
        return target

    target_norm = normalize_name(target)
    normalized_map = {name: normalize_name(name) for name in sessions}

    for name, norm in normalized_map.items():
        if norm == target_norm:
            return name

    substring_matches = [
        name for name, norm in normalized_map.items()
        if target_norm and (target_norm in norm or norm in target_norm)
    ]
    if len(substring_matches) == 1:
        return substring_matches[0]
    if len(substring_matches) > 1:
        substring_matches.sort(key=lambda item: (len(item), item))
        return substring_matches[0]

    scored = []
    for name, norm in normalized_map.items():
        score = difflib.SequenceMatcher(None, target_norm, norm).ratio()
        scored.append((score, name))
    scored.sort(reverse=True)
    if scored and scored[0][0] >= 0.45:
        return scored[0][1]

    return target


def score_name_match(query: str, candidate: str) -> float:
    query_norm = normalize_name(query)
    cand_norm = normalize_name(candidate)
    if not query_norm or not cand_norm:
        return 0.0
    if query_norm == cand_norm:
        return 1.0
    if query_norm in cand_norm or cand_norm in query_norm:
        return 0.9
    return difflib.SequenceMatcher(None, query_norm, cand_norm).ratio()


def choose_search_result(results: List[Any], query: str) -> Optional[Any]:
    ignored = {"最常使用", "群聊", "聊天记录"}
    filtered = []
    for item in results:
        content = str(getattr(item, "content", "") or "").strip()
        if not content or content in ignored or content.startswith("查看全部("):
            continue
        filtered.append((score_name_match(query, content), item, content))

    exact_matches = [row for row in filtered if normalize_name(row[2]) == normalize_name(query)]
    if exact_matches:
        return exact_matches[0][1]

    filtered.sort(key=lambda row: row[0], reverse=True)
    if filtered and filtered[0][0] >= 0.6:
        return filtered[0][1]
    return None


def search_result_contents(results: List[Any]) -> List[str]:
    contents: List[str] = []
    for item in results:
        content = str(getattr(item, "content", "") or "").strip()
        if content:
            contents.append(content)
    return contents


def open_chat(wx: Any, variant: str, who: str) -> str:
    switch_to_chat_page(wx)

    if variant == "wxauto4":
        try:
            results = wx.SessionBox.search(who) or []
        except Exception:
            results = []
        target = choose_search_result(list(results), who)
        if target is not None:
            content = str(getattr(target, "content", "") or who).strip()
            switched = False
            try:
                switch_by_search = getattr(wx.SessionBox, "_switch_chat_by_search", None)
                if callable(switch_by_search):
                    switch_by_search(content or who, exact=True, force=True, force_wait=0.8)
                    switched = True
            except Exception:
                switched = False

            if not switched:
                target.click()
            time.sleep(0.4)
            actual_chat = wait_current_chat_name(wx, variant, 2.0)
            if actual_chat and not (
                chat_name_matches(actual_chat, content) or chat_name_matches(actual_chat, who)
            ):
                raise WeChatSendError(
                    f"点击搜索结果后仍停留在其他会话，目标「{content or who}」，实际「{actual_chat}」"
                )
            return actual_chat or content or who

        try:
            sessions = wx.GetSession() or []
        except Exception as exc:
            print(f"[compat] failed to enumerate sessions, skip session click fallback: {exc}")
            sessions = []
        for session in sessions:
            name = str(getattr(session, "name", None) or getattr(session, "who", None) or "").strip()
            if name == who:
                try:
                    session.click()
                    time.sleep(0.4)
                    actual_chat = wait_current_chat_name(wx, variant, 2.0)
                    if actual_chat and not chat_name_matches(actual_chat, name):
                        raise WeChatSendError(
                            f"点击会话列表后仍停留在其他会话，目标「{name}」，实际「{actual_chat}」"
                        )
                    return actual_chat or name
                except Exception:
                    break

        preview = "、".join(search_result_contents(list(results))[:10])
        hint = [f"未能通过微信搜索定位到会话「{who}」。"]
        if preview:
            hint.append(f"当前搜索结果前 10 项: {preview}")
        hint.append("请确认联系人或群聊名称是否正确，或先在微信里手动打开一次该会话后再重试。")
        raise WeChatSendError("\n".join(hint))

    last_error: Optional[Exception] = None
    attempts = [
        lambda: wx.ChatWith(who, exact=True),
        lambda: wx.ChatWith(who, exact=False),
        lambda: wx.ChatWith(who, force=True, force_wait=0.8),
        lambda: wx.ChatWith(who),
    ]

    for attempt in attempts:
        try:
            attempt()
            time.sleep(0.4)
            actual_chat = wait_current_chat_name(wx, variant, 2.5)
            if actual_chat and not chat_name_matches(actual_chat, who):
                last_error = WeChatSendError(
                    f"切换会话后仍停留在其他会话，目标「{who}」，实际「{actual_chat}」"
                )
                continue
            return actual_chat or who
        except TypeError:
            try:
                wx.ChatWith(who)
                time.sleep(0.4)
                actual_chat = wait_current_chat_name(wx, variant, 2.5)
                if actual_chat and not chat_name_matches(actual_chat, who):
                    last_error = WeChatSendError(
                        f"切换会话后仍停留在其他会话，目标「{who}」，实际「{actual_chat}」"
                    )
                    continue
                return actual_chat or who
            except Exception as exc:
                last_error = exc
        except Exception as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise WeChatSendError(f"未能打开会话：{who}")


def message_attr(raw: Any) -> str:
    value = (
        getattr(raw, "attr", "") or
        getattr(raw, "type", "") or
        ""
    )
    return str(value).strip().lower()


def message_content(raw: Any) -> str:
    if isinstance(raw, (list, tuple)) and len(raw) >= 2:
        return str(raw[1] or "").strip()
    return str(getattr(raw, "content", "") or "").strip()


def message_sender(raw: Any) -> str:
    if isinstance(raw, (list, tuple)) and len(raw) >= 1:
        return str(raw[0] or "").strip()
    return str(getattr(raw, "sender", "") or "").strip()


def message_signature(raw: Any) -> str:
    return "|".join((message_attr(raw), message_sender(raw), message_content(raw)))


def get_messages_in_current_chat(wx: Any) -> List[Any]:
    try:
        return list(wx.GetAllMessage() or [])
    except Exception:
        return []


def get_raw_message_items(wx: Any) -> List[tuple[str, str]]:
    try:
        children = wx.ChatBox.msgbox.GetChildren() or []
    except Exception:
        return []

    result = []
    for child in children:
        class_name = str(getattr(child, "ClassName", "") or "").strip()
        content = str(getattr(child, "Name", "") or "").strip()
        if not content:
            continue
        result.append((class_name, content))
    return result


def count_matching_raw_items(items: List[tuple[str, str]], text: str) -> int:
    wanted = (text or "").strip()
    return sum(1 for _class_name, content in items if content == wanted)


def count_matching_messages(messages: List[Any], text: str) -> int:
    wanted = (text or "").strip()
    count = 0
    for raw in messages:
        if message_content(raw) != wanted:
            continue
        attr = message_attr(raw)
        if attr in {"self", "me", "send"} or not attr:
            count += 1
    return count


def verify_message_sent(wx: Any, variant: str, who: str, message: str, before: List[Any]) -> None:
    before_count = count_matching_messages(before, message)
    before_raw = count_matching_raw_items(get_raw_message_items(wx), message)
    deadline = time.time() + 8.0

    while time.time() < deadline:
        current_chat = current_chat_name(wx, variant)
        if current_chat and current_chat != who:
            time.sleep(0.3)
            continue

        after = get_messages_in_current_chat(wx)
        after_count = count_matching_messages(after, message)
        if after_count > before_count:
            return

        raw_items = get_raw_message_items(wx)
        raw_count = count_matching_raw_items(raw_items, message)
        if raw_count > before_raw:
            return

        if after:
            last = after[-1]
            if message_content(last) == message and message_attr(last) in {"self", "me", "send", ""}:
                return

        if raw_items and raw_items[-1][1] == message:
            return

        time.sleep(0.3)

    raise WeChatSendError(f"发送后未在对话框「{who}」中检测到消息内容：{message}")


def send_message(wx: Any, who: str, message: str, variant: str) -> None:
    before = get_messages_in_current_chat(wx)
    attempts = [
        lambda: wx.SendMsg(message),
        lambda: wx.SendMsg(message, who=who, exact=True),
        lambda: wx.SendMsg(message, who=who),
        lambda: wx.SendMsg(message, who),
    ]

    last_error: Optional[Exception] = None
    for attempt in attempts:
        try:
            attempt()
            verify_message_sent(wx, variant, who, message, before)
            return
        except Exception as exc:
            last_error = exc

    if last_error is not None:
        raise WeChatSendError(f"消息发送失败: {last_error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="通过桌面微信给指定联系人或群聊发消息")
    parser.add_argument("--who", help="联系人名或群聊名")
    parser.add_argument("--message", help="要发送的消息内容")
    parser.add_argument("--list-sessions", action="store_true", help="列出当前微信可见会话")
    parser.add_argument("--timeout", type=int, default=15, help="连接微信超时时间，默认 15 秒")
    parser.add_argument("--dry-run", action="store_true", help="只切到会话，不实际发送")
    return parser.parse_args()


def main() -> int:
    if os.name != "nt":
        raise WeChatSendError("该脚本仅支持 Windows。")

    args = parse_args()
    wxauto_module, variant = import_wechat_backend()
    wx = attach_wechat(wxauto_module, variant, args.timeout)

    if args.list_sessions:
        sessions = list_sessions(wx, variant)
        if not sessions:
            print("当前没有读取到任何微信会话。")
            return 0
        print("\n".join(sessions))
        return 0

    who = (args.who or "").strip()
    message = args.message if args.message is not None else ""
    if not who:
        raise WeChatSendError("缺少 --who 参数。")
    if not message:
        raise WeChatSendError("缺少 --message 参数，或消息内容为空。")

    resolved_who = resolve_target_chat_name(wx, variant, who)
    if resolved_who != who:
        print(f"[match] 输入名称「{who}」已模糊匹配到会话「{resolved_who}」")

    opened_chat = ""
    last_open_error: Optional[Exception] = None
    for retry_index in range(3):
        try:
            opened_candidate = open_chat(wx, variant, resolved_who)
        except Exception as exc:
            last_open_error = exc
            continue

        actual_chat = wait_current_chat_name(wx, variant, 2.0)
        if actual_chat and not (
            chat_name_matches(actual_chat, opened_candidate) or chat_name_matches(actual_chat, resolved_who)
        ):
            last_open_error = WeChatSendError(
                f"已打开的对话框不是目标会话，期望「{resolved_who}」，实际「{actual_chat}」"
            )
            print(f"[retry] 第 {retry_index + 1} 次切换后仍停留在「{actual_chat}」，继续重试")
            time.sleep(0.5)
            continue

        opened_chat = actual_chat or opened_candidate
        break

    if not opened_chat:
        available = list_sessions(wx, variant)
        hint = [f"未能切换到会话「{resolved_who}」: {last_open_error}"]
        if available:
            preview = "、".join(available[:20])
            hint.append(f"当前可见会话前 20 个: {preview}")
        hint.append("请确认会话名与微信里显示的一致，并且该会话已出现在最近会话列表。")
        raise WeChatSendError("\n".join(hint))

    if opened_chat != resolved_who:
        print(f"[match] 实际打开的会话为「{opened_chat}」")

    time.sleep(0.3)

    if args.dry_run:
        print(f"[dry-run] 已切到「{opened_chat}」，待发送内容: {message}")
        return 0

    send_message(wx, opened_chat, message, variant)
    print(f"已通过 {variant} 向「{opened_chat}」发送消息: {message}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WeChatSendError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
