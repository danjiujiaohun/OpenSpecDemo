# todo-management Specification

## Purpose
为个人用户在终端中提供待办事项的本地记录与回看能力，覆盖创建、查看、完成状态切换、删除，以及跨日期的历史查询。

## Requirements

### Requirement: 创建待办事项

用户 SHALL 能通过 `todo add <文本>` 创建一条待办，系统为其分配全局唯一且不复用的数字 id，并记录创建时间。

#### Scenario: 成功创建待办
- **WHEN** 用户执行 `todo add "写周报"`
- **THEN** 系统保存该待办，状态为未完成，创建时间为当前本地时间，并输出包含新 id 的确认信息

#### Scenario: 文本为空
- **WHEN** 用户执行 `todo add` 或传入空白文本
- **THEN** 系统不创建记录，输出错误提示并以非零状态码退出

### Requirement: 查看未完成待办

用户 SHALL 能通过 `todo list` 查看所有未完成待办，按创建日期分组，同组内按创建时间排序，并在末尾显示未完成总数。

#### Scenario: 跨天未完成事项
- **WHEN** 用户昨天创建了一条未完成待办，今天又创建了一条未完成待办，并执行 `todo list`
- **THEN** 系统按昨天的日期、今天的日期分两组显示两条待办，并显示未完成总数为 2

#### Scenario: 没有未完成待办
- **WHEN** 所有待办均已完成或列表中没有任何记录，用户执行 `todo list`
- **THEN** 系统不输出待办条目，并提示未完成数量为 0

### Requirement: 完成与撤销完成

用户 SHALL 能通过 `todo done <id>` 将指定待办标记为已完成并记录完成时间，并能通过 `todo undone <id>` 撤销完成状态。

#### Scenario: 标记完成
- **WHEN** 用户对一条未完成待办执行 `todo done <id>`
- **THEN** 该待办的完成时间被设置为当前本地时间，之后 `todo list` 不再显示它

#### Scenario: 重复标记完成
- **WHEN** 用户对一条已完成待办再次执行 `todo done <id>`
- **THEN** 系统保留原有完成时间不变，并提示该待办已完成

#### Scenario: 撤销完成
- **WHEN** 用户对一条已完成待办执行 `todo undone <id>`
- **THEN** 该待办的完成时间被清空，重新出现在 `todo list` 中

#### Scenario: id 不存在
- **WHEN** 用户执行 `todo done <id>` 或 `todo undone <id>` 且该 id 不存在
- **THEN** 系统不修改任何数据，输出错误提示并以非零状态码退出

### Requirement: 删除待办

用户 SHALL 能通过 `todo rm <id>` 删除指定待办，被删除的 id 不再出现在任何视图中且不会复用。

#### Scenario: 成功删除
- **WHEN** 用户对存在的待办执行 `todo rm <id>`
- **THEN** 该待办从存储中移除，`todo list` 与 `todo history` 均不再显示它

#### Scenario: 删除不存在的待办
- **WHEN** 用户对不存在的 id 执行 `todo rm <id>`
- **THEN** 系统不修改任何数据，输出错误提示并以非零状态码退出

### Requirement: 查看历史记录

用户 SHALL 能通过 `todo history` 查看全部待办（含已完成与未完成），按创建日期分组，并显示每条待办的创建时间与完成时间；也 SHALL 能通过 `todo history --date <YYYY-MM-DD>` 只查看指定创建日期分组的记录。

#### Scenario: 查看全部历史
- **WHEN** 用户执行 `todo history`
- **THEN** 系统按创建日期从新到旧显示全部待办，已完成项标记为完成并显示完成时间，未完成项标记为未完成

#### Scenario: 按日期筛选
- **WHEN** 用户执行 `todo history --date 2026-10-18`
- **THEN** 系统只显示创建日期为 2026-10-18 的待办

#### Scenario: 日期格式非法
- **WHEN** 用户执行 `todo history --date not-a-date`
- **THEN** 系统输出参数错误提示并以非零状态码退出

### Requirement: 本地数据持久化

系统 SHALL 将待办数据存储在用户级目录下的单个 JSON 文件中，首次运行时自动创建目录与文件，并在每次写操作后持久化，使后续命令能读到相同数据。

#### Scenario: 首次运行
- **WHEN** 用户首次执行任意 `todo` 命令且数据文件不存在
- **THEN** 系统自动创建数据目录与空数据文件，命令正常执行

#### Scenario: 数据跨命令保留
- **WHEN** 用户执行 `todo add` 后关闭终端，再次执行 `todo list`
- **THEN** 系统读取同一数据文件，显示之前添加的待办

#### Scenario: 数据文件损坏
- **WHEN** 数据文件内容不是合法 JSON
- **THEN** 系统输出明确的错误提示，不覆盖原文件，并以非零状态码退出
