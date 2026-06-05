#!/bin/sh

# 作用：
# 1. 批量编译并运行 examples/ 下的所有 VB 示例。
# 2. 生成与参考项目类似的结果目录：
#    - build/results_stdout/<name>_stdout/
#    - build/results_return/<name>/
# 3. 为每个示例保存 generated.c、stdout.txt、stderr.txt、exit.txt。
# 4. 生成 run_results.txt 作为总览汇总。

set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

RESULTS_STDOUT="$PROJECT_ROOT/build/results_stdout"
RESULTS_RETURN="$PROJECT_ROOT/build/results_return"
EXAMPLES_DIR="$PROJECT_ROOT/examples"

find_c_compiler() {
    if command -v clang >/dev/null 2>&1; then
        command -v clang
        return 0
    fi
    if command -v cc >/dev/null 2>&1; then
        command -v cc
        return 0
    fi
    return 1
}

preview_stdout() {
    file_path="$1"
    if [ ! -s "$file_path" ]; then
        printf '%s' "(no stdout)"
        return 0
    fi

    sed -n '1,6p' "$file_path" | tr '\n' '|' | sed 's/|$//'
}

run_example() {
    file_path="$1"
    compiler_path="$2"
    base_name="$(basename "$file_path" .vb)"

    stdout_dir="$RESULTS_STDOUT/${base_name}_stdout"
    return_dir="$RESULTS_RETURN/$base_name"

    mkdir -p "$stdout_dir" "$return_dir"

    PYTHONPATH="$PROJECT_ROOT/src" \
        python3 -m visual_basic_core_compiler "$file_path" --emit-c > "$stdout_dir/generated.c"

    cp "$stdout_dir/generated.c" "$return_dir/generated.c"

    "$compiler_path" "$stdout_dir/generated.c" -o "$stdout_dir/program"
    cp "$stdout_dir/program" "$return_dir/program"

    if "$stdout_dir/program" >"$stdout_dir/stdout.txt" 2>"$stdout_dir/stderr.txt"; then
        exit_code=0
    else
        exit_code=$?
    fi

    printf '%s\n' "$exit_code" > "$stdout_dir/exit.txt"

    cp "$stdout_dir/stdout.txt" "$return_dir/stdout.txt"
    cp "$stdout_dir/stderr.txt" "$return_dir/stderr.txt"
    cp "$stdout_dir/exit.txt" "$return_dir/exit.txt"

    stdout_preview="$(preview_stdout "$stdout_dir/stdout.txt")"
    printf '%s | exit=%s | stdout=%s\n' "$base_name" "$exit_code" "$stdout_preview" >> "$RESULTS_STDOUT/run_results.txt"
    printf '%s | exit=%s | stdout=%s\n' "$base_name" "$exit_code" "$stdout_preview" >> "$RESULTS_RETURN/run_results.txt"
}

main() {
    compiler_path="$(find_c_compiler)"
    mkdir -p "$RESULTS_STDOUT" "$RESULTS_RETURN"

    : > "$RESULTS_STDOUT/run_results.txt"
    : > "$RESULTS_RETURN/run_results.txt"

    find "$EXAMPLES_DIR" -maxdepth 1 -name '*.vb' | sort | while IFS= read -r file_path; do
        run_example "$file_path" "$compiler_path"
    done
}

main "$@"
