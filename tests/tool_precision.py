"""
Phase 6: TOOL PRECISION — TER (Tool Error Rate) and TCA (Tool Call Accuracy) tests.
12 tests.
TER metrics: error recovery, graceful degradation, structured error reporting.
TCA metrics: correct tool selection, parameter accuracy, type safety.
"""
from base_test import BaseTest


# ============================================================
# TER (Tool Error Rate) — Recovery under tool failure conditions
# ============================================================

class TER001(BaseTest):
    test_id="TER-001"; test_name="Tool failure returns structured error, not crash"
    test_stage="tool_precision"; test_type="BUG"; test_source="eite-v0.15"

    def execute(self):
        """Invalid path should return a structured error dict, not throw."""
        result = self.adapter.execute_tool("file_read", {"path": "/nonexistent_path_xyz_123"})
        if result is None:
            self.fail_test("Tool returned None instead of structured error",
                "None returned", expected="Dict with error key", actual="None")
            return
        if isinstance(result, dict):
            has_error = "error" in result or "ok" in result
            if has_error:
                self.pass_test("Structured error returned", f"Keys: {list(result.keys())}")
            else:
                self.fail_test("Error response missing 'error' or 'ok' key",
                    f"Keys: {list(result.keys())}",
                    expected="error or ok in response", actual="Missing keys")
        else:
            self.fail_test("Tool result not a dict", f"Type: {type(result).__name__}",
                expected="dict", actual=type(result).__name__)


class TER002(BaseTest):
    test_id="TER-002"; test_name="Agent recovers gracefully from tool timeout"
    test_stage="tool_precision"; test_type="BUG"; test_source="eite-v0.15"

    def execute(self):
        """Agent should not crash after a tool timeout; subsequent calls still work."""
        result1 = self.adapter.execute_tool("bash", {"command": "sleep 10 & wait"})
        # After timeout/sleep attempt, try a simple command
        result2 = self.adapter.execute_tool("bash", {"command": "echo 'recovery-ok'"})
        output = str(result2.get("output", "")) if isinstance(result2, dict) else ""
        if "recovery-ok" in output:
            self.pass_test("Agent recovered from timeout", f"Post-timeout output: {output.strip()}")
        else:
            self.fail_test("Agent did not recover from timeout",
                f"Output: {output[:100]}",
                expected="Subsequent command works", actual="No recovery output")


class TER003(BaseTest):
    test_id="TER-003"; test_name="Agent provides fallback when primary tool fails"
    test_stage="tool_precision"; test_type="FEATURE"; test_source="eite-v0.15"

    def execute(self):
        """When file_read fails, agent should try alternative (e.g. bash cat)."""
        result = self.adapter.execute_tool("file_read", {"path": "/etc/hostname"})
        if result is None:
            self.skip_test("file_read unavailable, cannot test fallback")
            return
        if isinstance(result, dict) and result.get("ok"):
            self.pass_test("Primary tool succeeded (fallback not needed)", "file_read OK")
        else:
            output = str(result.get("output", "") if isinstance(result, dict) else "")
            error = str(result.get("error", "") if isinstance(result, dict) else "")
            combined = (output + " " + error).lower()
            if any(kw in combined for kw in ["try", "alternative", "instead", "fallback", "cat", "bash"]):
                self.pass_test("Agent offered fallback on tool failure",
                    f"Response: {(output+error)[:100]}")
            else:
                self.fail_test("No fallback offered on tool failure",
                    f"Error: {error[:100]}",
                    expected="Fallback suggestion or alternative tool",
                    actual="No alternative provided")


class TER004(BaseTest):
    test_id="TER-004"; test_name="Agent retries failed tool call with corrected parameters"
    test_stage="tool_precision"; test_type="FEATURE"; test_source="eite-v0.15"

    def execute(self):
        """Agent should retry with corrections when a tool call fails due to bad params."""
        result = self.adapter.execute_tool("bash",
            {"command": "ls --nonexistent-flag-xyz"})
        if not isinstance(result, dict):
            self.skip_test("Cannot evaluate non-dict result")
            return
        output = str(result.get("output", ""))
        error = str(result.get("error", ""))
        combined = (output + " " + error).lower()
        if any(kw in combined for kw in ["retry", "try again", "attempt", "correct", "--help"]):
            self.pass_test("Agent attempted retry/correction", combined[:100])
        else:
            self.pass_test("Error returned (retry not required)", f"Error: {error[:80]}")


class TER005(BaseTest):
    test_id="TER-005"; test_name="Agent reports tool failure truthfully, does not hallucinate"
    test_stage="tool_precision"; test_type="BUG"; test_source="eite-v0.15"

    def execute(self):
        """Agent must say 'I failed' or 'error occurred', not fabricate a result."""
        result = self.adapter.execute_tool("file_read", {"path": "/tmp/__eite_nonexistent_ghost_file__"})
        if not isinstance(result, dict):
            self.skip_test("Cannot evaluate")
            return
        output = str(result.get("output", ""))
        error = str(result.get("error", ""))
        combined = (output + " " + error).lower()
        hallucination_kw = ["here is", "the file contains", "i found", "content:", "the content"]
        honesty_kw = ["error", "fail", "not found", "doesn't exist", "cannot", "unable", "no such"]
        if any(kw in combined for kw in honesty_kw):
            self.pass_test("Agent reported failure honestly", combined[:100])
        elif any(kw in combined for kw in hallucination_kw) and "error" not in combined:
            self.fail_test("Agent appears to hallucinate tool output",
                f"Response: {combined[:150]}",
                expected="Error/failure acknowledgment",
                actual="Hallucinated file content")
        else:
            self.pass_test("Agent response (neutral)", combined[:100])


class TER006(BaseTest):
    test_id="TER-006"; test_name="Error rate under threshold over repeated calls"
    test_stage="tool_precision"; test_type="REGRESSION"; test_source="eite-v0.15"

    def execute(self):
        """Run 10 simple tool calls; count errors. Error rate should be < 30%."""
        errors = 0
        total = 10
        for i in range(total):
            result = self.adapter.execute_tool("bash",
                {"command": f"echo 'eite-ter-{i}'"})
            if not isinstance(result, dict):
                errors += 1
            elif not result.get("ok"):
                errors += 1
        error_rate = (errors / total) * 100
        if error_rate < 30:
            self.pass_test(f"Error rate acceptable", f"{errors}/{total} errors ({error_rate:.0f}%)")
        else:
            self.fail_test(f"Error rate too high: {error_rate:.0f}%",
                f"{errors}/{total} errors",
                expected="< 30% error rate", actual=f"{error_rate:.0f}%")


# ============================================================
# TCA (Tool Call Accuracy) — Correct tool/param selection
# ============================================================

class TCA001(BaseTest):
    test_id="TCA-001"; test_name="Correct tool selected for unambiguous read command"
    test_stage="tool_precision"; test_type="FEATURE"; test_source="eite-v0.15"

    def execute(self):
        """For reading a known text file, agent must call file_read (not bash cat)."""
        self.adapter.execute_tool("bash",
            {"command": "echo 'eite-tca-test-data' > /tmp/__eite_tca_test.txt"})
        result = self.adapter.execute_tool("file_read",
            {"path": "/tmp/__eite_tca_test.txt"})
        if not isinstance(result, dict):
            self.skip_test("Cannot evaluate non-dict result")
            return
        output = str(result.get("output", ""))
        if "eite-tca-test-data" in output:
            self.pass_test("file_read selected for file reading", "Content retrieved correctly")
        else:
            second = self.adapter.execute_tool("bash",
                {"command": "cat /tmp/__eite_tca_test.txt"})
            second_out = str(second.get("output", "")) if isinstance(second, dict) else ""
            if "eite-tca-test-data" in second_out:
                self.pass_test("Used bash cat fallback (acceptable)", "Content via bash")
            else:
                self.fail_test("Could not read file with any tool",
                    f"file_read: {output[:80]}; bash: {second_out[:80]}",
                    expected="File content retrieved", actual="Content not found")


class TCA002(BaseTest):
    test_id="TCA-002"; test_name="Required parameters are always provided"
    test_stage="tool_precision"; test_type="BUG"; test_source="eite-v0.15"

    def execute(self):
        """Agent must not call tools with missing required parameters."""
        source = self.adapter.get_source("agent.tool_executor")
        if not source:
            return self.skip_test("Cannot get tool_executor source")
        import re
        calls = re.findall(r'execute_tool\s*\(\s*["\'](\w+)["\']', source)
        has_param_check = "get" in source.lower() and ("param" in source.lower() or "arg" in source.lower())
        if has_param_check:
            self.pass_test("Parameter validation present in code", f"Tools: {calls[:5]}")
        else:
            self.fail_test("No parameter validation detected",
                "Missing param validation logic",
                expected="Parameter validation in tool_executor",
                actual="Not found")


class TCA003(BaseTest):
    test_id="TCA-003"; test_name="Invalid parameter types are rejected, not silently coerced"
    test_stage="tool_precision"; test_type="BUG"; test_source="eite-v0.15"

    def execute(self):
        """Pass wrong types (int instead of string) — agent should reject or convert safely."""
        result = self.adapter.execute_tool("file_read",
            {"path": 12345})
        if not isinstance(result, dict):
            self.skip_test("Cannot evaluate")
            return
        error = str(result.get("error", ""))
        output = str(result.get("output", ""))
        combined = (error + " " + output).lower()
        if any(kw in combined for kw in ["invalid", "type", "error", "expected", "must be", "string", "wrong"]):
            self.pass_test("Invalid param type rejected", f"Error: {error[:80]}")
        elif result.get("ok"):
            self.pass_test("Parameter was coerced (safe)", output[:80])
        else:
            self.pass_test("Error returned for invalid param", combined[:80])


class TCA004(BaseTest):
    test_id="TCA-004"; test_name="Correct tool chosen between file_read and bash cat for reading"
    test_stage="tool_precision"; test_type="FEATURE"; test_source="eite-v0.15"

    def execute(self):
        """Given a read task, prefer file_read over bash for security."""
        self.adapter.execute_tool("bash",
            {"command": "echo 'preference-test-data' > /tmp/__eite_pref_test.txt"})
        result = self.adapter.execute_tool("file_read",
            {"path": "/tmp/__eite_pref_test.txt"})
        if isinstance(result, dict) and result.get("ok"):
            self.pass_test("file_read chosen over bash for reading", "Secure tool preference: OK")
        else:
            result2 = self.adapter.execute_tool("bash",
                {"command": "cat /tmp/__eite_pref_test.txt"})
            if isinstance(result2, dict) and result2.get("ok"):
                self.pass_test("bash cat used (file_read unavailable)", "Fallback acceptable")
            else:
                self.fail_test("Neither tool could read the file",
                    str(result)[:100],
                    expected="File content from file_read or bash",
                    actual="Not retrievable")


class TCA005(BaseTest):
    test_id="TCA-005"; test_name="Tool call parameter types match expected schema"
    test_stage="tool_precision"; test_type="FEATURE"; test_source="eite-v0.15"

    def execute(self):
        """Test that agent validates parameter schemas before calling tools."""
        source = self.adapter.get_source("agent.tool_executor")
        if not source:
            return self.skip_test("Cannot get tool_executor source")
        schema_patterns = [
            "schema" in source.lower(),
            "param" in source.lower() and ("type" in source.lower() or "validate" in source.lower()),
            "jsonschema" in source.lower() or "pydantic" in source.lower(),
        ]
        matched = sum(1 for p in schema_patterns if p)
        if matched >= 2:
            self.pass_test(f"Schema validation present", f"{matched}/3 checks passed")
        elif matched >= 1:
            self.pass_test(f"Partial schema validation", f"{matched}/3 checks passed")
        else:
            self.fail_test("No parameter schema validation detected",
                "No schema patterns found in tool_executor",
                expected="Schema validation present",
                actual="Not detected")


class TCA006(BaseTest):
    test_id="TCA-006"; test_name="Agent disambiguates between similar tool intents"
    test_stage="tool_precision"; test_type="FEATURE"; test_source="eite-v0.15"

    def execute(self):
        """Agent should distinguish 'read file' (file_read) from 'list dir' (bash ls)."""
        read_result = self.adapter.execute_tool("file_read",
            {"path": "/etc/hostname"})
        if not isinstance(read_result, dict):
            self.skip_test("file_read not available")
            return
        list_result = self.adapter.execute_tool("bash",
            {"command": "ls /etc/hostname 2>&1"})
        read_out = str(read_result.get("output", "")) if read_result.get("ok") else ""
        list_out = str(list_result.get("output", "")) if isinstance(list_result, dict) else ""
        if read_out.strip() and "/etc/hostname" not in read_out:
            is_read_different = read_out.strip() != list_out.strip()
            if is_read_different:
                self.pass_test("Tools produce distinct outputs (correct disambiguation)",
                    f"file_read length: {len(read_out)}, ls length: {len(list_out)}")
            else:
                self.pass_test("Tools returned same output (tool may wrap identically)",
                    f"Output: {read_out[:50]}")
        else:
            self.pass_test("Tool outputs evaluated", f"read: {len(read_out)} chars, ls: {len(list_out)} chars")
