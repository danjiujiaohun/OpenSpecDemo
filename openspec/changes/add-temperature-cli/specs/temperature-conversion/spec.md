# Spec Delta

## Purpose

为终端用户提供摄氏度与华氏度之间的双向数值换算，并给出可脚本化的输出格式、精度控制与输入边界校验。

## ADDED Requirements

### Requirement: 摄氏度转华氏度

用户 SHALL 能通过 `temp c2f <摄氏值>` 将摄氏度换算为华氏度，换算公式为 `F = C * 9 / 5 + 32`。

#### Scenario: 换算冰点

- **WHEN** 用户执行 `temp c2f 0`
- **THEN** 系统输出 `32 F` 并以状态码 0 退出

#### Scenario: 换算沸点

- **WHEN** 用户执行 `temp c2f 100`
- **THEN** 系统输出 `212 F` 并以状态码 0 退出

#### Scenario: 摄氏负温度

- **WHEN** 用户执行 `temp c2f -40`
- **THEN** 系统输出 `-40 F` 并以状态码 0 退出

### Requirement: 华氏度转摄氏度

用户 SHALL 能通过 `temp f2c <华氏值>` 将华氏度换算为摄氏度，换算公式为 `C = (F - 32) * 5 / 9`。

#### Scenario: 换算冰点

- **WHEN** 用户执行 `temp f2c 32`
- **THEN** 系统输出 `0 C` 并以状态码 0 退出

#### Scenario: 换算沸点

- **WHEN** 用户执行 `temp f2c 212`
- **THEN** 系统输出 `100 C` 并以状态码 0 退出

#### Scenario: 结果为循环小数

- **WHEN** 用户执行 `temp f2c 1`
- **THEN** 系统输出 `-17.2222 C` 并以状态码 0 退出

### Requirement: 默认输出格式

系统 SHALL 默认最多保留 4 位小数，并去除末尾的零和小数点；整数结果不带小数点。输出 SHALL 由数值、一个空格和单位 `C` 或 `F` 组成，且仅使用 ASCII 字符。

#### Scenario: 整数结果不带小数点

- **WHEN** 用户执行 `temp c2f 100`
- **THEN** 输出为 `212 F`，而不是 `212.0 F` 或 `212.0000 F`

#### Scenario: 非整数结果保留有效小数

- **WHEN** 用户执行 `temp c2f 37`
- **THEN** 输出为 `98.6 F`

#### Scenario: 负零归一化

- **WHEN** 用户执行 `temp f2c 31.99999999999999`
- **THEN** 输出为 `0 C`，而不是 `-0 C`

### Requirement: 精度控制

用户 SHALL 能通过 `--precision N` 覆盖默认的小数位数。`N` MUST 是 0 到 10 之间的整数；`N` 为 0 时结果四舍五入到整数，仍然去除小数部分。

#### Scenario: 指定两位小数

- **WHEN** 用户执行 `temp f2c --precision 2 1`
- **THEN** 系统输出 `-17.22 C` 并以状态码 0 退出

#### Scenario: 精度为 0

- **WHEN** 用户执行 `temp c2f --precision 0 37`
- **THEN** 系统输出 `99 F` 并以状态码 0 退出

#### Scenario: 精度超出范围

- **WHEN** 用户执行 `temp c2f --precision 11 100` 或 `temp c2f --precision -1 100`
- **THEN** 系统输出用法错误并以非零状态码退出

### Requirement: 无效数值处理

系统 MUST 拒绝无法解析为有限浮点数的输入，包括非数字文本、`nan` 和 `inf`。系统 SHALL 向 stderr 输出错误信息并以非零状态码退出，且不向 stdout 输出换算结果。

#### Scenario: 非数字文本

- **WHEN** 用户执行 `temp c2f abc`
- **THEN** stderr 包含 `数值无效`，stdout 为空，且退出码非零

#### Scenario: 非有限数值

- **WHEN** 用户执行 `temp c2f nan` 或 `temp f2c inf`
- **THEN** 系统报告数值无效并以非零状态码退出

### Requirement: 绝对零度校验

系统 MUST 拒绝低于绝对零度的输入：摄氏度低于 `-273.15` 或华氏度低于 `-459.67` 时，系统 SHALL 报告错误并以非零状态码退出；输入恰好等于绝对零度时 SHALL 被接受并正常换算。

#### Scenario: 摄氏度低于绝对零度

- **WHEN** 用户执行 `temp c2f -300`
- **THEN** stderr 包含 `绝对零度`，stdout 为空，且退出码非零

#### Scenario: 华氏度低于绝对零度

- **WHEN** 用户执行 `temp f2c -500`
- **THEN** stderr 包含 `绝对零度`，stdout 为空，且退出码非零

#### Scenario: 恰好等于绝对零度

- **WHEN** 用户执行 `temp c2f -273.15`
- **THEN** 系统输出 `-459.67 F` 并以状态码 0 退出

### Requirement: 结果范围校验

系统 MUST 在换算结果不是有限浮点数时拒绝输出，向 stderr 报告结果超出可表示范围，并以非零状态码退出。

#### Scenario: 结果溢出

- **WHEN** 用户执行 `temp c2f 1e308`
- **THEN** stderr 报告结果超出可表示范围，stdout 为空，且退出码非零

### Requirement: 命令行接口

系统 SHALL 提供 `c2f` 和 `f2c` 两个子命令。用户未提供子命令时，系统 SHALL 输出帮助信息并以状态码 0 退出；缺少数值参数或使用未知子命令时，系统 SHALL 输出用法错误并以非零状态码退出。

#### Scenario: 无子命令

- **WHEN** 用户执行 `temp`
- **THEN** 系统输出帮助信息并以状态码 0 退出

#### Scenario: 缺少数值参数

- **WHEN** 用户执行 `temp c2f`
- **THEN** 系统输出用法错误并以非零状态码退出

#### Scenario: 未知子命令

- **WHEN** 用户执行 `temp ftoc 100`
- **THEN** 系统输出用法错误并以非零状态码退出
