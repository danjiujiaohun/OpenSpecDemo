# Tasks

## 1. CLI 骨架与双向换算

- [x] 1.1 创建可执行脚本 `temp`（shebang、模块 docstring、`argparse` 主解析器与 `c2f` / `f2c` 子命令），验证 `./temp --help` 输出中文帮助、包含两个子命令，且退出码为 0
- [x] 1.2 实现 `c2f` 与 `f2c` 纯转换函数及子命令分发，验证 `./temp c2f 100` 输出 `212 F`、`./temp f2c 32` 输出 `0 C`
- [x] 1.3 新增 `tests/test_temp.py`，用子进程覆盖双向锚点（`0 C = 32 F`、`100 C = 212 F`、`-40 C = -40 F`、`37 C = 98.6 F`），验证 `python3 -m unittest tests.test_temp -v` 通过
- [x] 1.4 增加负数值位置参数用例 `./temp c2f -40`，验证输出 `-40 F` 且退出码为 0

## 2. 输出格式与精度

- [x] 2.1 实现结果格式化：最多 4 位小数、去除尾零与孤立小数点、负零归一化为 `0`，并补齐对应单元测试，验证整数结果精确等于 `212 F`、`1 F` 换算为 `-17.2222 C`
- [x] 2.2 实现 `--precision N`（0–10，默认 4），验证 `./temp f2c --precision 2 1` 输出 `-17.22 C`、`./temp c2f --precision 0 37` 输出 `99 F`
- [x] 2.3 为 `--precision` 的非法值（`11`、`-1`、非整数）补测试，验证均以非零状态码退出且 stdout 为空

## 3. 输入校验、错误语义与文档

- [x] 3.1 实现有限浮点解析，拒绝非数字、`nan`、`inf`，验证 `./temp c2f abc` 的 stderr 包含 `数值无效`、stdout 为空且退出码非零
- [x] 3.2 实现绝对零度校验，验证 `./temp c2f -300` 与 `./temp f2c -500` 报错退出，同时 `./temp c2f -273.15` 输出 `-459.67 F`
- [x] 3.3 实现换算结果有限性校验，验证 `./temp c2f 1e308` 报告结果超出可表示范围并非零退出
- [x] 3.4 补命令行形状测试：无子命令输出帮助且退出码 0，缺少数值参数与未知子命令均非零退出
- [x] 3.5 在 `README.md` 增加 `temp` 的安装、用法与输出示例，逐条运行文档中的示例命令，验证输出与文档一致

## 4. 集成验证

- [x] 4.1 运行完整测试套件 `python3 -m unittest discover -s tests -v`，验证新增测试与现有 `todo` 测试全部通过
- [x] 4.2 运行 `openspec validate add-temperature-cli --strict`，验证变更通过严格校验

## Workflow follow-up

- 实现与验证完成后，使用 `/opsx:apply add-temperature-cli` 推进任务，或在完成后运行 `openspec archive add-temperature-cli` 归档变更。
- 归档后检查 `openspec/specs/temperature-conversion/spec.md` 已生成且内容完整。
