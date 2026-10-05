# cryptarithm

字谜算术（alphametic）求解器：把 `SEND + MORE = MONEY` 这样的字母算式翻译成数字，
每个不同字母对应一个不同数字，首字母不能为 0。

纯标准库（argparse / sys / itertools），Python 3.10+。

## 用法

```bash
python -m cryptarithm "SEND + MORE = MONEY"
python -m cryptarithm "TWO + TWO = FOUR" --limit 3   # 只看前 3 个解
python -m cryptarithm "SEND + MORE = MONEY" --count  # 只数解的个数
python -m cryptarithm --examples                     # 内置例题
```

输出示例：

```
9567 + 1085 = 10652
```

## 设计取舍

- **逐列回溯 + 进位传播**，而不是对 10 个数字做全排列暴力：
  10P8 = 1,814,400 种排列，每种还要验算整个算式。
  逐列枚举每一列只涉及该列出现的字母（通常 ≤3 个），
  低位列一旦进位矛盾整棵子树被剪掉，典型题目的实际搜索量是暴力法的几百分之一。
- 支持多个加数（`A + B + C = D`），结果列可以比加数多一位（进位）。
- `--count` 不保存解，只计数，内存占用恒定。

## 已知局限

- 只做加法，不支持减法/乘法字谜。
- 不同字母超过 10 个直接判无解（这是数学上限，不是 bug）。
- 最坏情况仍是指数级的；10 个字母的难题可能需要几秒。
- 词中字母统一转大写，不区分大小写输入。
