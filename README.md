# todo

一个纯本地、单人使用的终端待办清单。零第三方依赖，只需要 Python 3。

- `todo list` 只看未完成事项，适合每天打开就用。
- `todo history` 回看全部记录和完成状态，支持按日期筛选。
- 数据保存在用户级目录的单个 JSON 文件里，方便备份和迁移。

## 安装

```bash
# 1. 让脚本可执行
chmod +x todo

# 2. 软链到 PATH 中的目录（这里用 ~/.local/bin）
mkdir -p ~/.local/bin
ln -sf "$PWD/todo" ~/.local/bin/todo

# 3. 如果 ~/.local/bin 不在 PATH，把下面一行加入 ~/.zshrc 后重开终端
export PATH="$HOME/.local/bin:$PATH"
```

验证：

```bash
todo --help
```

也可以直接运行仓库里的脚本，不安装：

```bash
./todo list
```

## 使用

```bash
todo add "写周报"                # 添加待办，返回 id
todo list                        # 查看所有未完成待办
todo done 3                      # 标记 #3 完成
todo undone 3                    # 撤销 #3 的完成状态
todo rm 3                        # 删除 #3
todo history                     # 查看全部记录
todo history --date 2026-10-19   # 只看某天创建的记录
```

输出示例：

```text
$ todo list
2026-10-19
  [ ]  1    写周报                   14:47
2026-10-18
  [ ]  2    买菜                     08:00

2 条未完成

$ todo history
2026-10-19
  [x]  1    写周报                   14:47 -> 17:30
  [ ]  3    整理桌面                 15:00
2026-10-18
  [ ]  2    买菜                     08:00

共 3 条记录
```

约定：

- id 单调递增，删除后不会复用。
- 未完成事项天然跨天延续，不需要「结转」。
- 日期分组按创建日期，从新到旧；同组内按创建时间排序。
- 输出为纯 ASCII、无颜色，便于复制、`grep` 和管道处理。

## 数据文件

位置按以下顺序解析：

1. `$XDG_DATA_HOME/todo/todos.json`（设置了且非空时）
2. `~/.local/share/todo/todos.json`

首次运行任意命令会自动创建目录和空数据文件。

备份或迁移：

```bash
cp ~/.local/share/todo/todos.json ~/todos-backup.json
# 迁移到新机器
mkdir -p ~/.local/share/todo && cp todos-backup.json ~/.local/share/todo/todos.json
```

如果数据文件内容损坏（不是合法 JSON 或结构不符），命令会报错退出，**不会覆盖原文件**。可以手工修复，或先备份后删除该文件让工具重新创建空数据：

```bash
mv ~/.local/share/todo/todos.json ~/.local/share/todo/todos.json.broken
todo list
```

## 温度换算（temp）

仓库还附带一个独立的温度换算命令 `temp`，与 `todo` 互不依赖，同样只使用 Python 标准库。

安装：

```bash
chmod +x temp
ln -sf "$PWD/temp" ~/.local/bin/temp
```

使用：

```bash
temp c2f 100                # 212 F
temp f2c 212                # 100 C
temp c2f 37                 # 98.6 F
temp f2c 1                  # -17.2222 C
temp f2c --precision 2 1    # -17.22 C
temp c2f --precision 0 37   # 99 F
```

约定：

- 默认最多保留 4 位小数，去掉尾零；整数结果不带小数点。
- 输出为纯 ASCII，数值与单位 `C` / `F` 之间以一个空格分隔。
- 输入无效、低于绝对零度或结果溢出时报错到 stderr，并以非零状态码退出。
- `nan`、`inf` 不作为有效温度。

也可以直接运行仓库里的脚本，不安装：

```bash
./temp c2f 100
```

## 测试

```bash
python3 -m unittest discover -s tests -v
```

`todo` 的测试通过临时 `XDG_DATA_HOME` 隔离数据，不会影响真实待办；`temp` 的测试不需要数据目录。
