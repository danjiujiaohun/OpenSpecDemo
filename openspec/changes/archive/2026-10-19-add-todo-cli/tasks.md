# Tasks

## 1. 脚本骨架与持久化层

- [x] 1.1 创建可执行入口脚本 `todo`，搭好 `argparse` 子命令骨架，验证 `./todo --help` 能列出全部子命令并以状态码 0 退出
- [x] 1.2 实现数据路径解析（优先 `XDG_DATA_HOME/todo/todos.json`，否则 `~/.local/share/todo/todos.json`）与首次运行自动建目录/空文件，验证 `tests/test_storage.py` 用临时 `XDG_DATA_HOME` 通过
- [x] 1.3 实现加载校验与原子保存（临时文件 + `os.replace`），验证合法数据往返一致、非法 JSON 报错且原文件未被覆盖

## 2. 待办命令实现

- [x] 2.1 实现 `todo add <text>`：分配单调递增 id、记录本地创建时间、拒绝空白文本，验证新增与空文本错误用例通过
- [x] 2.2 实现 `todo list`：只显示未完成项、按创建日期分组（新到旧）、组内按时间升序、输出未完成总数，验证跨天分组与空列表用例通过
- [x] 2.3 实现 `todo done <id>` / `todo undone <id>`：设置/清空完成时间，重复完成保留原完成时间，id 不存在时报错，验证对应用例通过
- [x] 2.4 实现 `todo rm <id>`：删除记录且 id 不复用，id 不存在时报错，验证对应用例通过
- [x] 2.5 实现 `todo history [--date YYYY-MM-DD]`：显示全部记录及完成状态，按日期筛选，非法日期报错，验证对应用例通过

## 3. 使用文档

- [x] 3.1 编写 `README.md`，说明安装（复制/软链到 `~/.local/bin`、`chmod +x`、PATH 配置）与全部命令示例，验证文档中的命令按原样执行可复现
- [x] 3.2 补充数据文件位置、备份/迁移与损坏恢复说明，验证与实现的路径解析行为一致

## 4. 集成验证

- [x] 4.1 在临时 `XDG_DATA_HOME` 下跑一遍完整生命周期（add → list → done → history → undone → rm），验证各步骤输出与状态符合规范
- [x] 4.2 运行全部单元测试与 `openspec validate add-todo-cli --strict`，验证两者均通过

## Workflow follow-up

- 实现完成并验证后，运行 `openspec archive add-todo-cli` 归档变更。
