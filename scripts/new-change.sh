#!/usr/bin/env bash
#
# 创建一个新的 OpenSpec 变更（需求）骨架，并打印下一步操作。
# 只创建变更目录与元数据，不生成规划文档、不写实现代码。

set -euo pipefail

usage() {
  cat <<'EOF'
用法:
  scripts/new-change.sh <change-name> ["需求描述"] [--goal "目标"]

示例:
  scripts/new-change.sh add-task-labels "给待办增加标签，并支持按标签筛选"
  scripts/new-change.sh add-task-labels --goal "支持标签筛选"

说明:
  - change-name 使用 kebab-case，例如 add-task-labels
  - 需求描述会写入该变更的 README.md
  - 脚本只创建变更骨架；规划文档在 Claude Code 中用 /opsx:propose 生成
EOF
}

if [[ $# -eq 0 ]]; then
  usage >&2
  exit 2
fi

case "$1" in
  -h|--help)
    usage
    exit 0
    ;;
esac

name="$1"
shift
description=""
goal=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --goal)
      [[ $# -ge 2 ]] || { echo "错误: --goal 缺少值" >&2; exit 2; }
      goal="$2"
      shift 2
      ;;
    --description)
      [[ $# -ge 2 ]] || { echo "错误: --description 缺少值" >&2; exit 2; }
      description="$2"
      shift 2
      ;;
    -*)
      echo "错误: 未知选项 $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      [[ -z "$description" ]] || { echo "错误: 多余参数 $1" >&2; exit 2; }
      description="$1"
      shift
      ;;
  esac
done

if ! [[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "错误: change 名称必须是 kebab-case（小写字母、数字、连字符），例如 add-task-labels" >&2
  exit 2
fi

if ! openspec list --json >/dev/null 2>&1; then
  echo "错误: 当前目录不在 OpenSpec 项目内，请先运行 openspec init" >&2
  exit 1
fi

args=(new change "$name")
[[ -n "$description" ]] && args+=(--description "$description")
[[ -n "$goal" ]] && args+=(--goal "$goal")

echo "==> 创建变更: $name"
openspec "${args[@]}" --json

echo
echo "==> 变更状态"
openspec status --change "$name" --json

echo
echo "==> 下一步"
echo "  1. 生成规划文档（把需求告诉 Claude，或使用 /opsx:propose）:"
echo "       如命令不可用，先恢复: openspec init --tools claude --no-animation"
echo "       然后运行: /opsx:propose $name"
echo "  2. 按 tasks.md 实现:"
echo "       /opsx:apply $name"
echo "  3. 验证并归档:"
echo "       openspec validate $name --strict"
echo "       openspec archive $name"
echo
echo "如需逐份查看写作说明:"
echo "  openspec instructions proposal --change $name --json"
