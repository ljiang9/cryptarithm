#!/usr/bin/env python3
"""cryptarithm: 字谜算术(alphametic)求解器.

把 "SEND + MORE = MONEY" 这样的字母算式翻译成数字,
每个不同字母对应一个不同数字, 首字母不能为 0.
"""
from __future__ import annotations

import argparse
import itertools
import sys


class PuzzleError(ValueError):
    """算式解析错误."""


def parse_puzzle(text: str) -> tuple[list[str], str]:
    """解析 "A + B = C" 形式, 返回 (加数字列表, 和).

    允许空格/小写, 只接受大写字母组成的单词.
    """
    cleaned = text.strip().upper().replace(" ", "")
    if "=" not in cleaned:
        raise PuzzleError("算式缺少 '=': %r" % text)
    left, _, right = cleaned.partition("=")
    if not left or not right:
        raise PuzzleError("等号两侧不能为空: %r" % text)
    addends = left.split("+")
    if any(not w or not w.isalpha() for w in addends):
        raise PuzzleError("加数必须是字母单词: %r" % text)
    if not right.isalpha():
        raise PuzzleError("结果必须是字母单词: %r" % text)
    words = addends + [right]
    letters = set("".join(words))
    if len(letters) > 10:
        raise PuzzleError("不同字母超过 10 个, 无解: %r" % text)
    if max(len(w) for w in addends) > len(right) > 0 and len(right) < max(
        len(w) for w in addends
    ):
        # 结果比最长加数还短, 不可能进位成立 (快速拒绝)
        raise PuzzleError("结果比加数还短, 无解: %r" % text)
    return addends, right


def solve(addends: list[str], result: str, limit: int | None = None):
    """按列从右到左回溯求解, yield 字母->数字 映射.

    逐列枚举 + 进位传播, 比 10P_n 暴力排列快得多:
    每一列只涉及该列出现的字母(通常 <=3 个), 大量分支在低位就被剪掉,
    典型题目的搜索量是暴力法的几百分之一.
    """
    leading = {w[0] for w in addends + [result]}
    maxlen = max([len(result)] + [len(w) for w in addends])
    # columns[i]: (加数字母列表, 结果字母或 None)
    columns = []
    for i in range(maxlen):
        adds = []
        for w in addends:
            if i < len(w):
                adds.append(w[-1 - i])
        res = result[-1 - i] if i < len(result) else None
        columns.append((adds, res))

    assignment: dict[str, int] = {}
    used = [False] * 10
    found = 0

    def candidates(letter: str):
        start = 1 if letter in leading else 0
        for d in range(start, 10):
            if not used[d]:
                yield d

    def backtrack(col: int, carry: int):
        nonlocal found
        if limit is not None and found >= limit:
            return
        if col == maxlen:
            if carry == 0:
                found += 1
                yield dict(assignment)
            return
        adds, res = columns[col]
        # 该列尚未赋值的字母(保持顺序, 去重)
        needed: list[str] = []
        for ch in adds + ([res] if res else []):
            if ch not in assignment and ch not in needed:
                needed.append(ch)

        def assign_needed(idx: int):
            nonlocal found
            if limit is not None and found >= limit:
                return
            if idx == len(needed):
                total = carry + sum(assignment[ch] for ch in adds)
                digit, new_carry = total % 10, total // 10
                if res is None:
                    if digit != 0:
                        return
                    yield from backtrack(col + 1, new_carry)
                    return
                rv = assignment[res]
                if rv == digit:
                    yield from backtrack(col + 1, new_carry)
                return
            ch = needed[idx]
            for d in candidates(ch):
                assignment[ch] = d
                used[d] = True
                yield from assign_needed(idx + 1)
                del assignment[ch]
                used[d] = False

        yield from assign_needed(0)

    yield from backtrack(0, 0)


def render(addends: list[str], result: str, mapping: dict[str, int]) -> str:
    def num(w: str) -> str:
        return "".join(str(mapping[ch]) for ch in w)

    return " + ".join(num(w) for w in addends) + " = " + num(result)


EXAMPLES = [
    "SEND + MORE = MONEY",
    "TWO + TWO = FOUR",
    "BASE + BALL = GAMES",
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="字谜算术求解器: 每个字母一个数字, 首字母不为 0."
    )
    ap.add_argument("puzzle", nargs="?", help='算式, 如 "SEND + MORE = MONEY"')
    ap.add_argument("--limit", type=int, default=None, help="最多输出几个解")
    ap.add_argument("--count", action="store_true", help="只输出解的个数")
    ap.add_argument("--examples", action="store_true", help="列出内置例题")
    args = ap.parse_args(argv)

    if args.examples:
        for ex in EXAMPLES:
            print(ex)
        return 0
    if not args.puzzle:
        ap.error("请给出一个算式, 或用 --examples 看例题")
    try:
        addends, result = parse_puzzle(args.puzzle)
    except PuzzleError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2

    if args.count:
        n = sum(1 for _ in solve(addends, result, limit=None))
        print("%d 个解" % n)
        return 0

    shown = 0
    for mapping in solve(addends, result, limit=args.limit):
        print(render(addends, result, mapping))
        shown += 1
    if shown == 0:
        print("无解")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
