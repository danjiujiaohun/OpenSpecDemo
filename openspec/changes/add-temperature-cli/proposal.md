# Proposal

## Why

日常在摄氏度与华氏度之间换算时，心算和临时搜索既慢又容易出错，也无法放进脚本。仓库已有零依赖、纯本地的命令行工具习惯，适合再提供一个可随手调用、可管道组合的换算命令。

## What Changes

- 新增独立可执行脚本 `temp`，与现有 `todo` 互不依赖。
- 提供两个方向子命令：`temp c2f <摄氏值>`、`temp f2c <华氏值>`。
- 输出默认最多 4 位小数、去除尾零、整数不带小数点，并带纯 ASCII 单位（`C` / `F`）。
- 支持 `--precision N` 覆盖小数位数（0–10）。
- 校验输入：拒绝非数字、`nan`、`inf`、非有限结果，以及低于绝对零度的温度；错误写 stderr 并以非零状态退出。
- 新增 `unittest` 测试，覆盖换算锚点、舍入、精度参数与错误路径。
- README 补充 `temp` 的安装与使用说明。

## Capabilities

### New Capabilities

- `temperature-conversion`: 摄氏度与华氏度的双向数值换算，包括输出格式、精度控制和输入边界校验。

### Modified Capabilities

无。现有 `todo-management` 的需求与行为不变。

## Impact

- 新增：`temp`（可执行脚本）、`tests/test_temp.py`、温度命令的测试辅助函数。
- 修改：`README.md` 增加 `temp` 的安装与用法。
- 依赖：无，仅使用 Python 3 标准库。
- 现有 `todo` 的命令、数据文件与测试不受影响。
