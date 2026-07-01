import subprocess
import tempfile
import os
import logging
from typing import List, Dict, Any
import inspect

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

    local_scope = {}

    try:
        exec(
            user_code,
            {"__builtins__": __builtins__},
            local_scope
        )

    except SyntaxError as se:
        return {
            "correct": False,
            "tests_passed": 0,
            "tests_total": total_tests,
            "compile_error": f"SyntaxError: {se}",
            "runtime_error": None,
        }

    except Exception as e:
        return {
            "correct": False,
            "tests_passed": 0,
            "tests_total": total_tests,
            "compile_error": f"Compilation Error: {e}",
            "runtime_error": None,
        }

    # -------------------------------------------------
    # Detect callable
    # -------------------------------------------------

    target_func = None

    # 1. Expected function
    if (
        function_name in local_scope
        and callable(local_scope[function_name])
    ):
        target_func = local_scope[function_name]

    # 2. LeetCode Solution class
    elif (
        "Solution" in local_scope
        and inspect.isclass(local_scope["Solution"])
    ):

        try:
            solution = local_scope["Solution"]()

            methods = [
                getattr(solution, name)
                for name in dir(solution)
                if callable(getattr(solution, name))
                and not name.startswith("__")
            ]

            if methods:
                target_func = methods[0]

        except Exception:
            pass

    # 3. First standalone function
    if target_func is None:

        functions = [
            obj
            for obj in local_scope.values()
            if inspect.isfunction(obj)
        ]

        if functions:
            target_func = functions[0]

    if target_func is None:
        return {
            "correct": False,
            "tests_passed": 0,
            "tests_total": total_tests,
            "compile_error": "No callable function found.",
            "runtime_error": None,
        }

    passed = 0

    for idx, tc in enumerate(test_cases):

        try:

            inputs = tc["input"]
            expected = tc["output"]

            signature = inspect.signature(target_func)

            params = list(signature.parameters.keys())

            # -------------------------------------
            # Try keyword arguments
            # -------------------------------------

            try:
                result = target_func(**inputs)

            except TypeError:

                # positional fallback

                if len(params) == len(inputs):
                    result = target_func(*inputs.values())

                elif len(params) == 1 and len(inputs) == 1:
                    result = target_func(
                        next(iter(inputs.values()))
                    )

                else:
                    raise

            # -------------------------------------
            # In-place problems
            # -------------------------------------

            if result is None:

                if len(inputs) == 1:
                    result = next(iter(inputs.values()))

                else:
                    result = tuple(inputs.values())

            # -------------------------------------
            # Debug
            # -------------------------------------

            logger.debug(
                "Function=%s Inputs=%s Expected=%s Got=%s",
                target_func.__name__,
                inputs,
                expected,
                result,
            )

            if result == expected:
                passed += 1

        except Exception as e:

            logger.exception(e)

            return {
                "correct": False,
                "tests_passed": passed,
                "tests_total": total_tests,
                "compile_error": None,
                "runtime_error": f"RuntimeError on testcase {idx+1}: {e}",
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
    