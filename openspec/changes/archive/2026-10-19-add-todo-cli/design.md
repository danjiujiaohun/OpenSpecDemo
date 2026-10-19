# Design

## Context

当前工作区只有 OpenSpec 配置，没有既有代码或技术栈约束。这是一个从零开始、单人本地使用的终端工具，规模小，目标是「小而完整」而非可扩展平台。行为要求见 `specs/todo-management/spec.md`，动机见 `proposal.md`。

## Goals / Non-Goals

**Goals:**
- 单文件、零第三方依赖、可直接执行的 Python CLI。
- 数据结构简单到可以手工阅读和备份。
- 清晰的终端输出，便于复制和管道处理。

**Non-Goals:**
- 不提供 TUI、交互式界面或颜色主题。
- 不支持多用户、云同步、提醒、标签、优先级、重复任务。
- 不追求并发写入下的强一致；只保证单次写入不产生半个文件。

## Decisions

### D1: Python 3 单文件脚本 + 标准库

使用 `argparse`、`json`、`datetime`、`pathlib`、`os` 实现，入口为仓库根目录下的可执行脚本 `todo`。

- 理由：运行环境已有 Python 3.13；零依赖意味着复制一个文件即可用，符合个人工具定位。
- 备选：Node/TypeScript（参数解析与类型样板更多）、Go/Rust（需编译与额外安装，当前环境未装）。

### D2: 子命令划分

```
todo add <text>
todo list
todo done <id>
todo undone <id>
todo rm <id>
todo history [--date YYYY-MM-DD]
```

- 理由：与用户已确认的交互模型一致；`list` 与 `history` 职责分离，主视图保持专注。
- 备选：单一 `todo` 加 flags（可读性差）、交互式 REPL（超出非目标）。

### D3: JSON 文件存储与位置

路径解析顺序：

1. `$XDG_DATA_HOME/todo/todos.json`（若设置且非空）
2. `~/.local/share/todo/todos.json`

文件结构：

```json
{
  "version": 1,
  "next_id": 2,
  "items": [
    {
      "id": 1,
      "text": "写周报",
      "created_at": "2026-10-19T09:12:00",
      "completed_at": null
    }
  ]
}
```

- `id` 由 `next_id` 单调分配，删除后不复用；`next_id` 随每次新增递增并持久化。
- `completed_at == null` 表示未完成。
- 时间使用本地时间、不带时区的 ISO 8601（`YYYY-MM-DDTHH:MM:SS`），使日期分组直观。
- 理由：单文件 JSON 可读、可备份，零依赖即可读写。备选 SQLite 对当前数据量过度设计。
- 写入采用「临时文件 + `os.replace`」保证原子替换；文件损坏时只报错、不覆盖。

### D4: 输出格式

- 纯 ASCII，无颜色、无 ANSI 控制符。
- 按创建日期分组，日期从新到旧；同组内按创建时间升序。
- 行格式：`  [x]  3  写周报        09:12 -> 17:30`（未完成省略 `->` 部分）。
- `list` 末尾输出 `N 条未完成`；`history` 末尾输出总条数。
- 理由：稳定、可复制、可被 `grep`/`awk` 处理。

### D5: 错误处理

- 参数错误、非法日期、id 不存在、数据文件损坏一律向 stderr 输出明确信息，并以非零状态码退出。
- 写操作失败时不留下部分修改：先在内存中完成变更，再原子写回。

### D6: 测试方式

使用标准库 `unittest`，通过 `subprocess` 调用脚本，并把 `XDG_DATA_HOME` 指向临时目录隔离测试数据。覆盖：增删改查、跨日期分组、日期筛选、错误路径、损坏文件。

## Risks / Trade-offs

- [并发写覆盖] 两个命令同时写可能后写覆盖先写 → 个人单人场景可接受；原子替换避免文件损坏，设计上不引入锁。
- [本地时间无时区] 跨时区迁移后历史日期可能偏移 → 明确接受，换取可读性；时间格式保留扩展空间。
- [JSON 全量读写] 数据量大时性能退化 → 个人待办量级下可忽略。
- [文本列宽] 长文本会破坏对齐 → 不截断文本，允许自然换行/变宽，优先保留完整信息。
