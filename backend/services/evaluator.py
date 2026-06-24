import subprocess
import tempfile
import os
import logging
from typing import List, Dict, Any

EXECUTION_TIMEOUT_SECONDS = 5
logger = logging.getLogger(__name__)

# =====================================================
# C++ Literal Conversion
# =====================================================

def cpp_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(value)
    if isinstance(value, str):
        # Escape quotes in string value
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, list):
        values = ", ".join(cpp_value(v) for v in value)
        return "{" + values + "}"
    if value is None:
        return "NULL"
    raise ValueError(f"Unsupported type: {type(value)}")


# =====================================================
# C++ Runner Builder
# =====================================================

def build_cpp_runner(
    user_code: str,
    function_name: str,
    test_cases: List[Dict[str, Any]],
    parameter_types: List[str],
    return_type: str
):
    tests = []

    for tc in test_cases:
        declarations = []
        arguments = []

        # Map each input value to its corresponding parameter type from the schema
        for idx, (name, value) in enumerate(tc["input"].items()):
            if idx < len(parameter_types):
                param_type = parameter_types[idx]
            else:
                # Fallback if parameter types mismatch
                if isinstance(value, list):
                    param_type = "vector<int>"
                elif isinstance(value, int):
                    param_type = "int"
                elif isinstance(value, bool):
                    param_type = "bool"
                elif isinstance(value, str):
                    param_type = "string"
                else:
                    param_type = "auto"
            
            declarations.append(f"{param_type} {name} = {cpp_value(value)};")
            arguments.append(name)

        args_str = ", ".join(arguments)
        expected_str = cpp_value(tc["output"])

        # We declare the expected variable with the correct return type
        ret_t = return_type if return_type and return_type != "void" else "auto"

        tests.append(
            f"""
            {{
                {" ".join(declarations)}
                auto result = {function_name}({args_str});
                {ret_t} expected = {expected_str};
                if (result == expected) {{
                    passed++;
                }}
            }}
            """
        )

    tests_code = "\n".join(tests)

    # Standard headers and helper types (e.g. TreeNode, ListNode if needed in future)
    return f"""
#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <algorithm>
#include <numeric>
#include <cmath>

using namespace std;

{user_code}

int main() {{
    int passed = 0;
    {tests_code}
    cout << passed;
    return 0;
}}
"""


# =====================================================
# Python Evaluator
# =====================================================

def run_python_tests(
    user_code: str,
    function_name: str,
    test_cases: List[Dict[str, Any]]
) -> Dict[str, Any]:
    total_tests = len(test_cases)
    
    # Sandboxed environment dictionary
    local_scope = {}
    try:
        # Execute user code in isolation
        exec(user_code, {"__builtins__": __builtins__}, local_scope)
    except SyntaxError as se:
        return {
            "correct": False,
            "tests_passed": 0,
            "tests_total": total_tests,
            "compile_error": f"SyntaxError: {str(se)}",
            "runtime_error": None,
        }
    except Exception as e:
        return {
            "correct": False,
            "tests_passed": 0,
            "tests_total": total_tests,
            "compile_error": f"Compilation Error: {str(e)}",
            "runtime_error": None,
        }

    if function_name not in local_scope:
        return {
            "correct": False,
            "tests_passed": 0,
            "tests_total": total_tests,
            "compile_error": f"NameError: function '{function_name}' is not defined.",
            "runtime_error": None,
        }

    target_func = local_scope[function_name]
    passed = 0

    for idx, tc in enumerate(test_cases):
        try:
            inputs = tc["input"]
            expected = tc["output"]
            
            # Call user's function with kwargs matching testcase input keys
            result = target_func(**inputs)
            
            if result == expected:
                passed += 1
        except Exception as e:
            return {
                "correct": False,
                "tests_passed": passed,
                "tests_total": total_tests,
                "compile_error": None,
                "runtime_error": f"RuntimeError on test case {idx + 1}: {str(e)}",
            }

    return {
        "correct": passed == total_tests,
        "tests_passed": passed,
        "tests_total": total_tests,
        "compile_error": None,
        "runtime_error": None,
    }


# =====================================================
# C++ Evaluator
# =====================================================

def run_cpp_tests(
    user_code: str,
    function_name: str,
    test_cases: List[Dict[str, Any]],
    parameter_types: List[str],
    return_type: str
) -> Dict[str, Any]:
    total_tests = len(test_cases)

    with tempfile.TemporaryDirectory() as tmpdir:
        cpp_file = os.path.join(tmpdir, "solution.cpp")
        exe_file = os.path.join(tmpdir, "solution")

        runner_code = build_cpp_runner(
            user_code,
            function_name,
            test_cases,
            parameter_types,
            return_type
        )

        with open(cpp_file, "w", encoding="utf-8") as f:
            f.write(runner_code)

        # Compile step
        compile_process = subprocess.run(
            ["g++", cpp_file, "-std=c++17", "-O2", "-o", exe_file],
            capture_output=True,
            text=True,
        )

        if compile_process.returncode != 0:
            return {
                "correct": False,
                "tests_passed": 0,
                "tests_total": total_tests,
                "compile_error": compile_process.stderr,
                "runtime_error": None,
            }

        # Execution step
        try:
            execution = subprocess.run(
                [exe_file],
                capture_output=True,
                text=True,
                timeout=EXECUTION_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return {
                "correct": False,
                "tests_passed": 0,
                "tests_total": total_tests,
                "compile_error": None,
                "runtime_error": "Time Limit Exceeded",
            }

        if execution.returncode != 0:
            return {
                "correct": False,
                "tests_passed": 0,
                "tests_total": total_tests,
                "compile_error": None,
                "runtime_error": execution.stderr or f"Exit status {execution.returncode}",
            }

        try:
            passed = int(execution.stdout.strip())
        except Exception:
            return {
                "correct": False,
                "tests_passed": 0,
                "tests_total": total_tests,
                "compile_error": None,
                "runtime_error": f"Invalid judge output: {execution.stdout}",
            }

        return {
            "correct": passed == total_tests,
            "tests_passed": passed,
            "tests_total": total_tests,
            "compile_error": None,
            "runtime_error": None,
        }


# =====================================================
# Unified Entry Point
# =====================================================

def run_tests(
    code: str,
    language: str,
    function_name: str,
    visible_testcases: List[Dict[str, Any]],
    hidden_testcases: List[Dict[str, Any]],
    parameter_types: List[str] = None,
    return_type: str = "auto"
) -> Dict[str, Any]:
    """
    Evaluates user DSA submissions in python/cpp.
    Returns:
        {
            "correct": bool,
            "tests_passed": int,
            "tests_total": int,
            "compile_error": str | None,
            "runtime_error": str | None
        }
    """
    test_cases = visible_testcases + hidden_testcases
    
    if not test_cases:
        return {
            "correct": True,
            "tests_passed": 0,
            "tests_total": 0,
            "compile_error": None,
            "runtime_error": None
        }

    if language.lower() in ("python", "py"):
        return run_python_tests(code, function_name, test_cases)
    else:
        # Default to C++
        ptypes = parameter_types if parameter_types is not None else []
        ret_t = return_type if return_type is not None else "auto"
        return run_cpp_tests(code, function_name, test_cases, ptypes, ret_t)