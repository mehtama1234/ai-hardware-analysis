"""Conservative lowering for the first generated SVA subset.

This is an explicit open-source compiler boundary. It accepts only bounded
property forms produced by the planner, including reset/hold/increment,
literal mappings, numeric invariants, and gated increments, and reports
unsupported syntax instead of silently dropping an assertion.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from pathlib import Path

from .planner import CheckPlan


PROPERTY_RE = re.compile(
    r"assert\s+property\s*\(\s*@\(posedge\s+(?P<clock>[A-Za-z_]\w*)\)\s*"
    r"(?:(?P<disable>disable\s+iff\s*\((?P<reset>[^)]+)\))\s*)?"
    r"(?P<body>.*?)\s*\)\s*;\s*$",
    re.S,
)


@dataclass(frozen=True)
class LoweredProperty:
    requirement_id: str
    original: str
    status: str
    clock: str | None
    reset: str | None
    lowered: str | None
    transformations: tuple[str, ...]
    reason: str | None = None

    def record(self) -> dict[str, object]:
        payload = asdict(self)
        payload["transformations"] = list(self.transformations)
        return payload


def lower_assertion(assertion: str, *, requirement_id: str) -> LoweredProperty:
    """Lower a supported generated assertion to an explicit clocked check."""
    match = PROPERTY_RE.fullmatch(assertion.strip())
    if not match:
        return LoweredProperty(requirement_id, assertion, "unsupported", None, None, None, (), "assertion is outside the supported clocked subset")
    clock = match["clock"]
    reset = match["reset"].strip() if match["reset"] else None
    body = " ".join(match["body"].split())
    guard = f" && !({reset})" if reset else ""
    transformations = ["clock_alias_injection"]
    if reset:
        transformations.append("disable_iff_extraction")

    hold = re.fullmatch(r"!enable\s*\|=>\s*\$stable\((?P<signal>[A-Za-z_]\w*)\)", body)
    if hold:
        transformations.append("sequence_delay_lowering")
        signal = hold["signal"]
        lowered = (
            f"always @(posedge {clock}) begin\n"
            f"  if (previous_valid{guard} && !enable && {signal} !== previous_{signal}) $error(\"{requirement_id}: hold violated\");\n"
            f"  previous_{signal} <= {signal};\n"
            "  previous_valid <= 1'b1;\n"
            "end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    increment = re.fullmatch(r"enable\s*\|=>\s*(?P<signal>[A-Za-z_]\w*)\s*==\s*\$past\((?P<past>[A-Za-z_]\w*)\)\s*\+\s*1'b1", body)
    if increment and increment["signal"] == increment["past"]:
        transformations.append("sequence_delay_lowering")
        signal = increment["signal"]
        lowered = (
            f"always @(posedge {clock}) begin\n"
            f"  if (previous_valid{guard} && enable && {signal} !== previous_{signal} + 1'b1) $error(\"{requirement_id}: increment violated\");\n"
            f"  previous_{signal} <= {signal};\n"
            "  previous_valid <= 1'b1;\n"
            "end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    delayed_response = re.fullmatch(r"(?P<first>!?[A-Za-z_]\w*)\s*\|->\s*##\s*(?P<delay>[1-9]\d*)\s*(?P<consequent>!?[A-Za-z_]\w*)", body)
    if delayed_response:
        transformations.extend(["sequence_delay_lowering", "sequence_history_register"])
        delay = int(delayed_response["delay"])
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        sequence = f"sequence_{history}"
        first = delayed_response["first"]
        consequent = delayed_response["consequent"]
        lowered = (
            f"logic [{delay - 1}:0] {sequence};\n"
            f"always @(posedge {clock}) begin\n"
            + (f"  if ({reset}) {sequence} <= '0;\n  else begin\n" if reset else "  begin\n")
            + f"    if ({sequence}[{delay - 1}] && !({consequent})) $error(\"{requirement_id}: delayed response violated\");\n"
            + f"    {sequence}[0] <= {first};\n"
            + (f"    for (integer delay_i = 1; delay_i < {delay}; delay_i = delay_i + 1) {sequence}[delay_i] <= {sequence}[delay_i - 1];\n  end\n" if delay > 1 else "  end\n")
            + "end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    bounded_response = re.fullmatch(r"(?P<first>!?[A-Za-z_]\w*)\s*\|->\s*##\s*\[1\s*:\s*(?P<maximum>[1-9]\d*)\]\s*(?P<consequent>!?[A-Za-z_]\w*)", body)
    if bounded_response:
        maximum = int(bounded_response["maximum"])
        if maximum > 16:
            return LoweredProperty(requirement_id, assertion, "unsupported", clock, reset, None, tuple(transformations), "bounded response exceeds the lowering limit of 16 cycles")
        transformations.extend(["bounded_response_window_lowering", "response_window_register"])
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        active = f"response_active_{history}"
        satisfied = f"response_satisfied_{history}"
        first = bounded_response["first"]
        consequent = bounded_response["consequent"]
        reset_body = f"if ({reset}) begin {active} <= '0; {satisfied} <= '0; end\n  else begin\n" if reset else "begin\n"
        lowered = (
            f"logic [{maximum - 1}:0] {active};\n"
            f"logic [{maximum - 1}:0] {satisfied};\n"
            f"always @(posedge {clock}) begin\n"
            f"  {reset_body}"
            f"    if ({active}[{maximum - 1}] && !{satisfied}[{maximum - 1}] && !({consequent})) $error(\"{requirement_id}: bounded response violated\");\n"
            f"    {active}[0] <= {first};\n"
            f"    {satisfied}[0] <= 1'b0;\n"
            + ("".join(f"    {active}[{index}] <= {active}[{index - 1}];\n    {satisfied}[{index}] <= {satisfied}[{index - 1}] || ({active}[{index - 1}] && {consequent});\n" for index in range(1, maximum)) if maximum > 1 else "")
            + "  end\nend"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    bounded_until = re.fullmatch(r"(?P<first>!?[A-Za-z_]\w*)\s*\|->\s*(?P=first)\[\*\s*0\s*:\s*(?P<maximum_minus_one>[0-9]\d*)\s*\]\s*##\s*\[1\s*:\s*(?P<maximum>[1-9]\d*)\]\s*(?P<consequent>!?[A-Za-z_]\w*)", body)
    if bounded_until:
        maximum = int(bounded_until["maximum"])
        if maximum != int(bounded_until["maximum_minus_one"]) + 1:
            return LoweredProperty(requirement_id, assertion, "unsupported", clock, reset, None, tuple(transformations), "bounded until range is inconsistent")
        if maximum > 16:
            return LoweredProperty(requirement_id, assertion, "unsupported", clock, reset, None, tuple(transformations), "bounded until exceeds the lowering limit of 16 cycles")
        transformations.extend(["bounded_until_lowering", "until_pending_register"])
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        pending = f"until_pending_{history}"
        age = f"until_age_{history}"
        first = bounded_until["first"]
        consequent = bounded_until["consequent"]
        reset_body = f"if ({reset}) begin {pending} <= 1'b0; {age} <= 0; end\n  else begin\n" if reset else "begin\n"
        lowered = (
            f"logic {pending};\n"
            f"integer {age};\n"
            f"always @(posedge {clock}) begin\n"
            f"  {reset_body}"
            f"    if ({pending}) begin\n"
            f"      if ({consequent}) begin {pending} <= 1'b0; {age} <= 0; end\n"
            f"      else if (!({first}) || {age} == {maximum - 1}) begin $error(\"{requirement_id}: bounded until violated\"); {pending} <= 1'b0; {age} <= 0; end\n"
            f"      else {age} <= {age} + 1;\n"
            f"    end else if ({first} && !({consequent})) begin {pending} <= 1'b1; {age} <= 0; end\n"
            f"  end\nend"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    delayed_sequence = re.fullmatch(r"(?P<first>!?[A-Za-z_]\w*)\s*##\s*(?P<delay>[1-9]\d*)\s*(?P<second>!?[A-Za-z_]\w*)\s*\|->\s*(?P<consequent>!?[A-Za-z_]\w*)", body)
    if delayed_sequence:
        transformations.extend(["sequence_delay_lowering", "sequence_history_register"])
        delay = int(delayed_sequence["delay"])
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        sequence = f"sequence_{history}"
        first = delayed_sequence["first"]
        second = delayed_sequence["second"]
        consequent = delayed_sequence["consequent"]
        lowered = (
            f"logic [{delay - 1}:0] {sequence};\n"
            f"always @(posedge {clock}) begin\n"
            + (f"  if ({reset}) {sequence} <= '0;\n  else begin\n" if reset else "  begin\n")
            + f"    if ({sequence}[{delay - 1}] && {second} && !({consequent})) $error(\"{requirement_id}: delayed sequence implication violated\");\n"
            + f"    {sequence}[0] <= {first};\n"
            + (f"    for (integer delay_i = 1; delay_i < {delay}; delay_i = delay_i + 1) {sequence}[delay_i] <= {sequence}[delay_i - 1];\n  end\n" if delay > 1 else "  end\n")
            + "end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    repetition = re.fullmatch(r"(?P<signal>!?[A-Za-z_]\w*)\s*\[\*\s*(?P<count>[1-9]\d*)\s*\]\s*\|->\s*(?P<consequent>!?[A-Za-z_]\w*)", body)
    if repetition:
        transformations.extend(["consecutive_repetition_lowering", "repetition_counter_lowering"])
        count = int(repetition["count"])
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        counter = f"repetition_{history}"
        signal = repetition["signal"]
        consequent = repetition["consequent"]
        reset_body = f"if ({reset}) {counter} <= 0;\n    else " if reset else ""
        lowered = (
            f"integer {counter};\n"
            f"always @(posedge {clock}) begin\n"
            f"  {reset_body}begin\n"
            f"    if ({signal}) begin\n"
            f"      if ({counter} == {count - 1}) begin\n"
            f"        if (!({consequent})) $error(\"{requirement_id}: repetition implication violated\");\n"
            f"        {counter} <= 0;\n"
            f"      end else {counter} <= {counter} + 1;\n"
            f"    end else {counter} <= 0;\n"
            "  end\n"
            "end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    reset_check = re.fullmatch(r"(?P<signal>[A-Za-z_]\w*)\s*\|->\s*(?P<rhs>[A-Za-z_]\w*)\s*==\s*'0", body)
    if reset_check and reset_check["signal"] in {reset, "rst"}:
        transformations.append("reset_guard_lowering")
        signal = reset_check["rhs"]
        lowered = f"always @(posedge {clock}) begin\n  if ({reset_check['signal']} && {signal} !== '0) $error(\"{requirement_id}: reset invariant violated\");\nend"
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    onehot = re.fullmatch(r"\$(?P<kind>onehot0?)\((?P<signal>[A-Za-z_]\w*)\)", body)
    if onehot:
        transformations.append("onehot_predicate_lowering")
        guard = f" && !({reset})" if reset else ""
        lowered = (
            f"always @(posedge {clock}) begin\n"
            f"  if (!${onehot['kind']}({onehot['signal']}){guard}) "
            f"$error(\"{requirement_id}: {onehot['kind']} predicate violated\");\nend"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    mutual_exclusion = re.fullmatch(r"!\((?P<left>[A-Za-z_]\w*)\s*&&\s*(?P<right>[A-Za-z_]\w*)\)", body)
    if mutual_exclusion:
        transformations.append("mutual_exclusion_predicate_lowering")
        left, right = mutual_exclusion["left"], mutual_exclusion["right"]
        lowered = (
            f"always @(posedge {clock}) begin\n"
            f"  if (({left} && {right}){guard}) $error(\"{requirement_id}: mutual exclusion violated\");\nend"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    literal_mapping = re.fullmatch(
        r"(?P<input>[A-Za-z_]\w*)\s*==\s*(?P<input_value>\d+'[bdho][0-9a-fA-F_xz]+)\s*\|->\s*"
        r"(?P<output>[A-Za-z_]\w*)\s*==\s*(?P<output_value>\d+'[bdho][0-9a-fA-F_xz]+)", body,
    )
    if literal_mapping:
        transformations.append("literal_mapping_lowering")
        guard = f" && !({reset})" if reset else ""
        lowered = (
            f"always @(posedge {clock}) begin\n"
            f"  if ({literal_mapping['input']} == {literal_mapping['input_value']}{guard} && "
            f"{literal_mapping['output']} !== {literal_mapping['output_value']}) "
            f"$error(\"{requirement_id}: literal mapping violated\");\nend"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    invariant = re.fullmatch(r"(?P<signal>[A-Za-z_]\w*)\s*(?P<operator><=|>=|<|>)\s*(?P<value>\d+)", body)
    if invariant:
        transformations.append("bounded_invariant_lowering")
        guard = f" && !({reset})" if reset else ""
        lowered = (
            f"always @(posedge {clock}) begin\n"
            f"  if (!({invariant['signal']} {invariant['operator']} {invariant['value']}){guard}) "
            f"$error(\"{requirement_id}: invariant violated\");\nend"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    gated_increment = re.fullmatch(
        r"(?P<enable>[A-Za-z_]\w*)\s*&&\s*(?P<signal>[A-Za-z_]\w*)\s*<\s*(?P<limit>\d+)\s*\|=>\s*"
        r"(?P<next>[A-Za-z_]\w*)\s*==\s*\$past\((?P<past>[A-Za-z_]\w*)\)\s*\+\s*1'b1", body,
    )
    if gated_increment and gated_increment["signal"] == gated_increment["next"] == gated_increment["past"]:
        transformations.extend(["compound_boolean_implication_lowering", "one_cycle_delay_lowering"])
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        signal, enable, limit = gated_increment["signal"], gated_increment["enable"], gated_increment["limit"]
        reset_body = (
            f"  if ({reset}) begin previous_valid_{history} <= 1'b0; previous_{history}_value <= '0; end\n"
            "  else begin\n" if reset else ""
        )
        close_body = "  end\n" if reset else ""
        lowered = (
            f"logic previous_valid_{history};\n"
            f"logic [31:0] previous_{history}_value;\n"
            f"always @(posedge {clock}) begin\n"
            f"{reset_body}"
            f"    if (previous_valid_{history} && {enable} && {signal} < {limit} && "
            f"{signal} !== previous_{history}_value + 1'b1) $error(\"{requirement_id}: gated increment violated\");\n"
            f"    previous_{history}_value <= {signal};\n"
            f"    previous_valid_{history} <= 1'b1;\n"
            f"{close_body}end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    compound_implication = re.fullmatch(
        r"(?P<antecedent>\(?!?[A-Za-z_]\w*(?:\s*(?:&&|\|\|)\s*!?[A-Za-z_]\w*)+\)?)\s*"
        r"(?P<operator>\|->|\|=>)\s*(?P<consequent>!?[A-Za-z_]\w*)",
        body,
    )
    if compound_implication:
        transformations.append("compound_boolean_implication_lowering")
        antecedent = compound_implication["antecedent"].strip()
        if antecedent.startswith("(") and antecedent.endswith(")"):
            antecedent = antecedent[1:-1].strip()
        consequent = compound_implication["consequent"]
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        guard = f" && !({reset})" if reset else ""
        if compound_implication["operator"] == "|=>":
            transformations.append("one_cycle_delay_lowering")
            lowered = (
                f"always @(posedge {clock}) begin\n"
                f"  if (previous_{history}{guard} && !({consequent})) $error(\"{requirement_id}: compound implication violated\");\n"
                f"  previous_{history} <= ({antecedent});\n"
                "end"
            )
        else:
            lowered = (
                f"always @(posedge {clock}) begin\n"
                f"  if (({antecedent}){guard} && !({consequent})) $error(\"{requirement_id}: compound implication violated\");\n"
                "end"
            )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    implication = re.fullmatch(r"(?P<antecedent>!?[A-Za-z_]\w*)\s*(?P<operator>\|->|\|=>)\s*(?P<consequent>!?[A-Za-z_]\w*)", body)
    if implication:
        transformations.append("boolean_implication_lowering")
        antecedent = implication["antecedent"]
        consequent = implication["consequent"]
        guard = f" && !({reset})" if reset else ""
        if implication["operator"] == "|=>":
            transformations.append("one_cycle_delay_lowering")
            history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
            lowered = (
                f"always @(posedge {clock}) begin\n"
                f"  if (previous_{history}{guard} && !({consequent})) $error(\"{requirement_id}: implication violated\");\n"
                f"  previous_{history} <= {antecedent};\n"
                "end"
            )
        else:
            lowered = (
                f"always @(posedge {clock}) begin\n"
                f"  if ({antecedent}{guard} && !({consequent})) $error(\"{requirement_id}: implication violated\");\n"
                "end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    ranged_repetition = re.fullmatch(r"(?P<signal>!?[A-Za-z_]\w*)\s*\[\*\s*(?P<minimum>[1-9]\d*)\s*:\s*(?P<maximum>[1-9]\d*)\s*\]\s*\|->\s*(?P<consequent>!?[A-Za-z_]\w*)", body)
    if ranged_repetition:
        minimum = int(ranged_repetition["minimum"])
        maximum = int(ranged_repetition["maximum"])
        if minimum > maximum:
            return LoweredProperty(requirement_id, assertion, "unsupported", clock, reset, None, ("clock_alias_injection",), "repetition minimum exceeds maximum")
        transformations.extend(["bounded_repetition_lowering", "repetition_counter_lowering"])
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        counter = f"repetition_{history}"
        signal = ranged_repetition["signal"]
        consequent = ranged_repetition["consequent"]
        reset_body = f"if ({reset}) {counter} <= 0;\n    else " if reset else ""
        lowered = (
            f"integer {counter};\n"
            f"always @(posedge {clock}) begin\n"
            f"  {reset_body}begin\n"
            f"    if ({signal}) begin\n"
            f"      if ({counter} >= {minimum - 1} && {counter} < {maximum}) begin\n"
            f"        if (!({consequent})) $error(\"{requirement_id}: bounded repetition implication violated\");\n"
            "      end\n"
            f"      if ({counter} == {maximum - 1}) {counter} <= 0;\n"
            f"      else {counter} <= {counter} + 1;\n"
            f"    end else {counter} <= 0;\n"
            "  end\n"
            "end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    ranged_nonconsecutive = re.fullmatch(r"(?P<signal>!?[A-Za-z_]\w*)\s*\[(?P<kind>=|->)\s*(?P<minimum>[1-9]\d*)\s*:\s*(?P<maximum>[1-9]\d*)\s*\]\s*\|->\s*(?P<consequent>!?[A-Za-z_]\w*)", body)
    if ranged_nonconsecutive:
        minimum = int(ranged_nonconsecutive["minimum"])
        maximum = int(ranged_nonconsecutive["maximum"])
        if minimum > maximum:
            return LoweredProperty(requirement_id, assertion, "unsupported", clock, reset, None, tuple(transformations), "repetition minimum exceeds maximum")
        transformations.extend(["ranged_nonconsecutive_repetition_lowering", "repetition_counter_lowering"])
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        counter = f"occurrences_{history}"
        signal = ranged_nonconsecutive["signal"]
        consequent = ranged_nonconsecutive["consequent"]
        reset_body = f"if ({reset}) {counter} <= 0;\n    else " if reset else ""
        lowered = (
            f"integer {counter};\n"
            f"always @(posedge {clock}) begin\n"
            f"  {reset_body}begin\n"
            f"    if ({signal}) begin\n"
            f"      if ({counter} >= {minimum - 1} && {counter} < {maximum}) begin\n"
            f"        if (!({consequent})) $error(\"{requirement_id}: ranged non-consecutive repetition implication violated\");\n"
            "      end\n"
            f"      if ({counter} == {maximum - 1}) {counter} <= 0;\n"
            f"      else {counter} <= {counter} + 1;\n"
            f"    end\n"
            "  end\n"
            "end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    nonconsecutive = re.fullmatch(r"(?P<signal>!?[A-Za-z_]\w*)\s*\[(?P<kind>=|->)\s*(?P<count>[1-9]\d*)\s*\]\s*\|->\s*(?P<consequent>!?[A-Za-z_]\w*)", body)
    if nonconsecutive:
        transformations.extend(["nonconsecutive_repetition_lowering", "repetition_counter_lowering"])
        count = int(nonconsecutive["count"])
        history = re.sub(r"[^A-Za-z0-9_]", "_", requirement_id)
        counter = f"occurrences_{history}"
        signal = nonconsecutive["signal"]
        consequent = nonconsecutive["consequent"]
        reset_body = f"if ({reset}) {counter} <= 0;\n    else " if reset else ""
        lowered = (
            f"integer {counter};\n"
            f"always @(posedge {clock}) begin\n"
            f"  {reset_body}begin\n"
            f"    if ({signal}) begin\n"
            f"      if ({counter} == {count - 1}) begin\n"
            f"        if (!({consequent})) $error(\"{requirement_id}: non-consecutive repetition implication violated\");\n"
            f"        {counter} <= 0;\n"
            f"      end else {counter} <= {counter} + 1;\n"
            f"    end\n"
            "  end\n"
            "end"
        )
        return LoweredProperty(requirement_id, assertion, "supported", clock, reset, lowered, tuple(transformations))

    return LoweredProperty(requirement_id, assertion, "unsupported", clock, reset, None, tuple(transformations), f"unsupported property body: {body}")


def lower_plans(plans: list[CheckPlan]) -> list[LoweredProperty]:
    return [lower_assertion(plan.assertion, requirement_id=plan.requirement_id) for plan in plans]


def generate_lowered_checker(properties: list[LoweredProperty], *, module_name: str = "lowered_checks") -> str:
    """Emit a compile-oriented checker for the counter subset.

    Unsupported properties are emitted as comments and are intentionally
    counted in the manifest; they cannot become a passing verification claim.
    """
    if not module_name.isidentifier():
        raise ValueError("module name must be an identifier")
    known = {"assert", "property", "posedge", "disable", "iff", "past", "stable", "onehot", "onehot0", "and", "or", "not", "if", "else", "clk", "rst", "enable", "counter_q"}
    extra_signals = sorted({token for property_ in properties for token in re.findall(r"\b[A-Za-z_]\w*\b", property_.original) if token not in known})
    ports = ["input logic clk", "input logic rst", "input logic enable", "input logic [3:0] counter_q"]
    ports.extend(f"input logic {signal}" for signal in extra_signals)
    history_names = sorted({match.group(1) for property_ in properties for match in re.finditer(r"previous_([A-Za-z0-9_]+)", property_.lowered or "") if match.group(1) != "valid" and not match.group(1).startswith("valid_")})
    declared_names = {
        match.group(1) for property_ in properties
        for match in re.finditer(r"\blogic(?:\s*\[[^]]+\])?\s+(previous_[A-Za-z0-9_]+)\s*;", property_.lowered or "")
    }
    lines = ["// Generated explicit SVA lowering; unsupported properties are not executable.", f"module {module_name}({', '.join(ports)});"]
    lines.extend(f"  logic [3:0] previous_{name};" if name == "counter_q" else f"  logic previous_{name};" for name in history_names if f"previous_{name}" not in declared_names)
    lines.append("  logic previous_valid;")
    initial_values = " ".join(f"previous_{name} = '0;" for name in history_names if f"previous_{name}" not in declared_names)
    lines.append(f"  initial begin {initial_values} previous_valid = 1'b0; end")
    for property_ in properties:
        lines.append(f"  // requirement: {property_.requirement_id} status={property_.status}")
        if property_.status != "supported":
            lines.append(f"  // BLOCKED: {property_.reason}")
            continue
        body = property_.lowered or ""
        body = body.replace("previous_counter_q", "previous_counter_q")
        lines.extend("  " + line for line in body.splitlines())
    lines.extend(["endmodule", ""])
    return "\n".join(lines)


def write_lowering_manifest(properties: list[LoweredProperty], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {"schema_version": "sva-lowering-v1", "properties": [item.record() for item in properties]}
    payload["lowering_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
