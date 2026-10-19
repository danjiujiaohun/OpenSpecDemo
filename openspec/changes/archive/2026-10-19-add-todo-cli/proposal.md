# Proposal

## Why

日常在终端工作时，需要一个零依赖、纯本地、单人使用的待办工具，随手记录任务并跨天回看历史完成情况，而不必打开浏览器或引入服务端。

## What Changes

- 新增 `todo` 命令行工具，支持添加、查看、完成/撤销完成、删除待办。
- `todo list` 只显示未完成事项，并按创建日期分组；`todo history` 显示全部记录，可按日期筛选。
- 数据保存在用户级位置的单个 JSON 文件中，首次运行自动创建。
- 工具为单文件 Python 脚本，仅使用标准库，无需安装第三方依赖。

## Capabilities

### New Capabilities

- `todo-management`: 待办记录的生命周期管理，包括创建、列表展示、完成状态切换、删除与历史回看。

### Modified Capabilities

<!-- 无：当前项目没有既有 capability。 -->

## Impact

- 新增 `todo` 可执行脚本（Python 3.13，仅标准库）。
- 新增数据目录与文件：`~/.local/share/todo/todos.json`（遵循 `XDG_DATA_HOME`）。
- 无第三方依赖，不影响其他系统。
