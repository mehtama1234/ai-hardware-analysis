"""Validated register specifications and deterministic collateral generation.

All frontends target the same small JSON-compatible IR.  Unsupported
SystemRDL constructs are rejected rather than silently approximated.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
import re
from typing import Any
import xml.etree.ElementTree as ET


ACCESS = {"RW", "RO", "W1C"}
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class RegisterField:
    name: str
    lsb: int
    width: int
    access: str
    reset: int = 0
    description: str = ""

    @property
    def msb(self) -> int:
        return self.lsb + self.width - 1


@dataclass(frozen=True)
class Register:
    name: str
    offset: int
    width: int
    reset: int
    fields: tuple[RegisterField, ...]


@dataclass(frozen=True)
class RegisterSpec:
    name: str
    data_width: int
    addr_width: int
    registers: tuple[Register, ...]
    schema_version: str = "register-spec-v1"

    def validate(self) -> None:
        if self.schema_version != "register-spec-v1":
            raise ValueError("unsupported register specification schema")
        if not IDENTIFIER.fullmatch(self.name):
            raise ValueError(f"invalid block name: {self.name}")
        if self.data_width <= 0 or self.data_width % 8:
            raise ValueError("data_width must be a positive multiple of eight")
        if self.addr_width <= 0:
            raise ValueError("addr_width must be positive")
        names: set[str] = set()
        offsets: set[int] = set()
        max_value = (1 << self.data_width) - 1
        max_offset = (1 << self.addr_width) - 1
        for register in self.registers:
            if not IDENTIFIER.fullmatch(register.name):
                raise ValueError(f"invalid register name: {register.name}")
            if register.name in names:
                raise ValueError(f"duplicate register name: {register.name}")
            if register.offset in offsets:
                raise ValueError(f"duplicate register offset: {register.offset}")
            if register.offset < 0 or register.offset > max_offset or register.offset % (self.data_width // 8):
                raise ValueError(f"register offset is invalid or unaligned: {register.name}")
            if register.width != self.data_width:
                raise ValueError(f"register width must equal data_width: {register.name}")
            if register.reset < 0 or register.reset > max_value:
                raise ValueError(f"register reset is out of range: {register.name}")
            names.add(register.name)
            offsets.add(register.offset)
            used: set[int] = set()
            for field in register.fields:
                if not IDENTIFIER.fullmatch(field.name):
                    raise ValueError(f"invalid field name: {register.name}.{field.name}")
                if field.width <= 0 or field.lsb < 0 or field.msb >= self.data_width:
                    raise ValueError(f"field range is invalid: {register.name}.{field.name}")
                if field.access not in ACCESS:
                    raise ValueError(f"unsupported access policy: {register.name}.{field.name}")
                field_mask = set(range(field.lsb, field.msb + 1))
                if used & field_mask:
                    raise ValueError(f"overlapping fields: {register.name}.{field.name}")
                used |= field_mask
                if field.reset < 0 or field.reset >= (1 << field.width):
                    raise ValueError(f"field reset is out of range: {register.name}.{field.name}")
                if (register.reset & ((1 << field.width) - 1) << field.lsb) != field.reset << field.lsb:
                    raise ValueError(f"field reset disagrees with register reset: {register.name}.{field.name}")
        if not self.registers:
            raise ValueError("register specification must contain at least one register")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def digest(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class RegisterShadow:
    """Deterministic scoreboard model for generated register semantics."""

    def __init__(self, spec: RegisterSpec):
        spec.validate()
        self.spec = spec
        self.values = {register.offset: register.reset for register in spec.registers}

    def reset(self) -> None:
        self.values = {register.offset: register.reset for register in self.spec.registers}

    def _register(self, address: int) -> Register:
        for register in self.spec.registers:
            if register.offset == address:
                return register
        raise KeyError(f"unmapped register address: 0x{address:X}")

    @staticmethod
    def _field_value(value: int, field: RegisterField) -> int:
        return (value >> field.lsb) & ((1 << field.width) - 1)

    def read(self, address: int) -> int:
        self._register(address)
        return self.values[address]

    def write(self, address: int, data: int) -> int:
        register = self._register(address)
        if data < 0 or data >= (1 << self.spec.data_width):
            raise ValueError("write data is out of range")
        value = self.values[address]
        for field in register.fields:
            mask = ((1 << field.width) - 1) << field.lsb
            incoming = self._field_value(data, field)
            if field.access == "RW":
                value = (value & ~mask) | (incoming << field.lsb)
            elif field.access == "W1C":
                value &= ~(incoming << field.lsb)
        self.values[address] = value
        return value


def load_register_spec(path: str | Path) -> RegisterSpec:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("register specification must be an object")
    registers: list[Register] = []
    for raw_register in payload.get("registers", []):
        if not isinstance(raw_register, dict):
            raise ValueError("register entry must be an object")
        fields = tuple(RegisterField(
            name=str(raw_field["name"]),
            lsb=int(raw_field["lsb"]),
            width=int(raw_field["width"]),
            access=str(raw_field["access"]),
            reset=int(raw_field.get("reset", 0)),
            description=str(raw_field.get("description", "")),
        ) for raw_field in raw_register.get("fields", []))
        registers.append(Register(
            name=str(raw_register["name"]),
            offset=int(raw_register["offset"]),
            width=int(raw_register.get("width", payload.get("data_width", 32))),
            reset=int(raw_register.get("reset", 0)),
            fields=fields,
        ))
    spec = RegisterSpec(
        name=str(payload.get("name", "")),
        data_width=int(payload.get("data_width", 0)),
        addr_width=int(payload.get("addr_width", 0)),
        registers=tuple(registers),
        schema_version=str(payload.get("schema_version", "")),
    )
    spec.validate()
    return spec


def _local(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(element) if child.tag.rsplit("}", 1)[-1] == name]


def _text(element: ET.Element, name: str, *, required: bool = True) -> str | None:
    matches = [child for child in element.iter() if child.tag.rsplit("}", 1)[-1] == name]
    if not matches or not (matches[0].text or "").strip():
        if required:
            raise ValueError(f"IP-XACT element is missing {name}")
        return None
    return (matches[0].text or "").strip()


def _number(value: str, label: str) -> int:
    try:
        return int(value, 0)
    except ValueError as exc:
        raise ValueError(f"IP-XACT {label} is not an integer: {value}") from exc


def _access(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]", "", value.lower())
    if normalized in {"readwrite", "rw"}:
        return "RW"
    if normalized in {"readonly", "ro"}:
        return "RO"
    if normalized in {"write1toclear", "writeonetoclear", "w1c"}:
        return "W1C"
    raise ValueError(f"unsupported IP-XACT access policy: {value}")


def load_ipxact_spec(path: str | Path, *, name: str | None = None, data_width: int = 32, addr_width: int = 16) -> RegisterSpec:
    """Load the small register subset common to IP-XACT 2014 documents."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"invalid IP-XACT XML: {exc}") from exc
    component_name = name or _text(root, "name", required=False) or Path(path).stem
    width_text = _text(root, "dataWidth", required=False)
    if width_text:
        data_width = _number(width_text, "dataWidth")
    registers: list[Register] = []
    register_nodes = [element for element in root.iter() if element.tag.rsplit("}", 1)[-1] == "register"]
    if not register_nodes:
        raise ValueError("IP-XACT document contains no registers")
    for register_node in register_nodes:
        register_name = _text(register_node, "name")
        offset_text = _text(register_node, "addressOffset")
        width_node = _text(register_node, "size", required=False)
        register_width = _number(width_node, "size") if width_node else data_width
        field_nodes = [element for element in register_node if element.tag.rsplit("}", 1)[-1] == "field"]
        if not field_nodes:
            raise ValueError(f"IP-XACT register has no fields: {register_name}")
        fields: list[RegisterField] = []
        register_reset = 0
        for field_node in field_nodes:
            field_name = _text(field_node, "name")
            bit_offset = _number(_text(field_node, "bitOffset"), "bitOffset")
            bit_width = _number(_text(field_node, "bitWidth"), "bitWidth")
            # IP-XACT permits the field access element to be omitted; the
            # default software access policy is read-write. Explicit but
            # unknown policies still go through _access() and are rejected.
            access_text = _text(field_node, "access", required=False) or "read-write"
            reset_value = _text(field_node, "value", required=False)
            reset = _number(reset_value, "reset value") if reset_value else 0
            field = RegisterField(field_name, bit_offset, bit_width, _access(access_text), reset)
            fields.append(field)
            register_reset |= reset << bit_offset
        registers.append(Register(register_name, _number(offset_text, "addressOffset"), register_width, register_reset, tuple(fields)))
    spec = RegisterSpec(component_name, data_width, addr_width, tuple(registers))
    spec.validate()
    return spec


def _systemrdl_number(value: str, label: str) -> int:
    try:
        return int(value.strip().replace("_", ""), 0)
    except ValueError as exc:
        raise ValueError(f"SystemRDL {label} is not an integer: {value.strip()}") from exc


def _systemrdl_body(text: str, start: int, label: str) -> tuple[str, int]:
    """Return one balanced brace body and the index after its closing brace."""
    if start >= len(text) or text[start] != "{":
        raise ValueError(f"SystemRDL {label} is missing a body")
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:index], index + 1
    raise ValueError(f"SystemRDL {label} has an unbalanced body")


def _systemrdl_property(body: str, name: str, *, required: bool = False) -> str | None:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*([^;]+);", body, re.I)
    if not match:
        if required:
            raise ValueError(f"SystemRDL field is missing {name}")
        return None
    return match.group(1).strip()


def _systemrdl_access(body: str) -> str:
    access = (_systemrdl_property(body, "access") or _systemrdl_property(body, "sw") or "rw").lower()
    onwrite = (_systemrdl_property(body, "onwrite") or "").lower()
    if access in {"r", "ro"}:
        return "RO"
    if access in {"rw", "wr", "readwrite"}:
        return "W1C" if onwrite in {"wclr", "w1c", "clear"} else "RW"
    if access in {"w1c", "woclr", "wclr"} or onwrite in {"wclr", "w1c", "clear"}:
        return "W1C"
    raise ValueError(f"unsupported SystemRDL access policy: {access}")


def load_systemrdl_spec(path: str | Path, *, name: str | None = None, data_width: int = 32, addr_width: int = 16) -> RegisterSpec:
    """Load a conservative SystemRDL subset into :class:`RegisterSpec`.

    Supported forms are ``addrmap`` plus ``reg`` declarations containing
    ``field`` blocks with explicit bit ranges and ``sw``/``access``,
    ``onwrite``, and ``reset`` properties.  Register offsets may be explicit
    with ``@``; otherwise registers are packed on data-width byte boundaries.
    The parser rejects arrays, external components, dynamic addressing, and
    fields without a recoverable range.
    """
    source = Path(path).read_text(encoding="utf-8")
    source = re.sub(r"//[^\n]*|/\*.*?\*/", "", source, flags=re.S)
    addrmap = re.search(r"\baddrmap\s+(?P<name>[A-Za-z_]\w*)\s*\{", source)
    if not addrmap:
        raise ValueError("SystemRDL document must contain one addrmap body")
    map_body, _ = _systemrdl_body(source, source.find("{", addrmap.start()), "addrmap")
    component_name = name or addrmap.group("name")
    map_width = re.search(r"\b(?:regwidth|datawidth)\s*=\s*([^;]+);", map_body, re.I)
    if map_width:
        data_width = _systemrdl_number(map_width.group(1), "data width")
    registers: list[Register] = []
    cursor = 0
    register_pattern = re.compile(r"\breg\s+(?P<name>[A-Za-z_]\w*)\s*(?:@\s*(?P<offset>[^\s{]+))?\s*\{")
    position = 0
    while True:
        match = register_pattern.search(map_body, position)
        if not match:
            break
        body, end = _systemrdl_body(map_body, map_body.find("{", match.start()), f"register {match.group('name')}")
        offset = _systemrdl_number(match.group("offset"), "register offset") if match.group("offset") else cursor
        fields: list[RegisterField] = []
        field_pattern = re.compile(
            r"\bfield\s*(?:(?P<leading>[A-Za-z_]\w*)\s*)?\{(?P<body>.*?)\}\s*"
            r"(?P<trailing>[A-Za-z_]\w*)\s*\[(?P<msb>\d+)\s*:\s*(?P<lsb>\d+)\]",
            re.S,
        )
        for field_match in field_pattern.finditer(body):
            field_body = field_match.group("body")
            field_name = field_match.group("trailing") or field_match.group("leading")
            if not field_name:
                raise ValueError(f"SystemRDL field in register {match.group('name')} has no name")
            msb, lsb = int(field_match.group("msb")), int(field_match.group("lsb"))
            if msb < lsb:
                raise ValueError(f"SystemRDL field range is reversed: {field_name}")
            reset_text = _systemrdl_property(field_body, "reset")
            reset = _systemrdl_number(reset_text, "field reset") if reset_text else 0
            fields.append(RegisterField(field_name, lsb, msb - lsb + 1, _systemrdl_access(field_body), reset))
        if not fields:
            raise ValueError(f"SystemRDL register has no supported ranged fields: {match.group('name')}")
        register_reset = sum(field.reset << field.lsb for field in fields)
        registers.append(Register(match.group("name"), offset, data_width, register_reset, tuple(fields)))
        cursor = offset + data_width // 8
        position = end
    if not registers:
        raise ValueError("SystemRDL addrmap contains no supported registers")
    spec = RegisterSpec(component_name, data_width, addr_width, tuple(registers))
    spec.validate()
    return spec


def _range(field: RegisterField) -> str:
    return str(field.lsb) if field.width == 1 else f"{field.msb}:{field.lsb}"


def generate_register_rtl(spec: RegisterSpec) -> str:
    spec.validate()
    module = f"{spec.name}_regs"
    ports = ["input logic clk", "input logic rst", "input logic wr_en", f"input logic [{spec.addr_width - 1}:0] addr", f"input logic [{spec.data_width - 1}:0] wdata"]
    ports.extend(f"output logic [{spec.data_width - 1}:0] {register.name}" for register in spec.registers)
    lines = [f"// Generated from register-spec-v1 digest {spec.digest()}", f"module {module}({', '.join(ports)});", "  always_ff @(posedge clk) begin", "    if (rst) begin"]
    for register in spec.registers:
        lines.append(f"      {register.name} <= {spec.data_width}'h{register.reset:x};")
    lines.extend(["    end else if (wr_en) begin", "      case (addr)"])
    for register in spec.registers:
        lines.append(f"        {spec.addr_width}'d{register.offset}: begin")
        for field in register.fields:
            lines.append(f"          // field {register.name}.{field.name}[{_range(field)}] access={field.access}")
            if field.access == "RW":
                lines.append(f"          {register.name}[{_range(field)}] <= wdata[{_range(field)}];")
            elif field.access == "W1C":
                lines.append(f"          {register.name}[{_range(field)}] <= {register.name}[{_range(field)}] & ~wdata[{_range(field)}];")
        lines.append("        end")
    lines.extend(["        default: begin end", "      endcase", "    end", "  end", "endmodule", ""])
    return "\n".join(lines)


def generate_c_header(spec: RegisterSpec) -> str:
    spec.validate()
    guard = re.sub(r"[^A-Za-z0-9]", "_", spec.name).upper() + "_REGS_H"
    lines = [f"/* Generated from register-spec-v1 digest {spec.digest()} */", f"#ifndef {guard}", f"#define {guard}", ""]
    for register in spec.registers:
        lines.append(f"#define {spec.name.upper()}_{register.name.upper()}_OFFSET 0x{register.offset:X}u")
        for field in register.fields:
            prefix = f"{spec.name.upper()}_{register.name.upper()}_{field.name.upper()}"
            lines.extend([f"#define {prefix}_LSB {field.lsb}u", f"#define {prefix}_WIDTH {field.width}u", f"#define {prefix}_RESET 0x{field.reset:X}u", f"#define {prefix}_ACCESS_{field.access} 1u"])
    lines.extend(["", f"#endif /* {guard} */", ""])
    return "\n".join(lines)


def generate_uvm_ral_model(spec: RegisterSpec) -> str:
    spec.validate()
    block = f"{spec.name}_ral"
    lines = [f"// Deterministic UVM RAL metadata generated from register-spec-v1 digest {spec.digest()}", f"class {block} extends uvm_reg_block;", "  `uvm_object_utils(%s)" % block, "", f"  function new(string name=\"{block}\");", "    super.new(name, UVM_NO_COVERAGE);", "  endfunction", "", "  // Register metadata is intentionally explicit for review and adapter binding."]
    for register in spec.registers:
        lines.append(f"  // {register.name}: offset=0x{register.offset:X}, reset=0x{register.reset:X}")
        for field in register.fields:
            lines.append(f"  //   {field.name}[{_range(field)}] access={field.access} reset=0x{field.reset:X}")
    lines.extend(["endclass", ""])
    return "\n".join(lines)


def generate_scoreboard(spec: RegisterSpec) -> str:
    """Generate a standalone synthesizable-style register scoreboard."""
    spec.validate()
    module = f"{spec.name}_register_scoreboard"
    ports = ["input logic clk", "input logic rst", "input logic wr_en", f"input logic [{spec.addr_width - 1}:0] addr", f"input logic [{spec.data_width - 1}:0] wdata"]
    ports.extend(f"input logic [{spec.data_width - 1}:0] actual_{register.name}" for register in spec.registers)
    ports.append("output logic mismatch")
    lines = [f"// Generated register scoreboard from register-spec-v1 digest {spec.digest()}", f"module {module}({', '.join(ports)});"]
    lines.extend(f"  logic [{spec.data_width - 1}:0] expected_{register.name};" for register in spec.registers)
    lines.extend(["  always_ff @(posedge clk) begin", "    if (rst) begin"])
    lines.extend(f"      expected_{register.name} <= {spec.data_width}'h{register.reset:x};" for register in spec.registers)
    lines.extend(["    end else if (wr_en) begin", "      case (addr)"])
    for register in spec.registers:
        lines.append(f"        {spec.addr_width}'d{register.offset}: begin")
        for field in register.fields:
            rng = _range(field)
            lines.append(f"          // field {register.name}.{field.name}[{rng}] access={field.access}")
            if field.access == "RW":
                lines.append(f"          expected_{register.name}[{rng}] <= wdata[{rng}];")
            elif field.access == "W1C":
                lines.append(f"          expected_{register.name}[{rng}] <= expected_{register.name}[{rng}] & ~wdata[{rng}];")
        lines.append("        end")
    lines.extend(["        default: begin end", "      endcase", "    end"])
    comparisons = " || ".join(f"(actual_{register.name} !== expected_{register.name})" for register in spec.registers)
    lines.extend([f"    mismatch <= {comparisons};", "  end", "endmodule", ""])
    return "\n".join(lines)


def write_register_bundle(spec: RegisterSpec, output_dir: str | Path) -> dict[str, Any]:
    spec.validate()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    files = {
        "rtl": (output / f"{spec.name}_regs.sv", generate_register_rtl(spec)),
        "c_header": (output / f"{spec.name}_regs.h", generate_c_header(spec)),
        "uvm_ral": (output / f"{spec.name}_ral.sv", generate_uvm_ral_model(spec)),
        "scoreboard": (output / f"{spec.name}_scoreboard.sv", generate_scoreboard(spec)),
    }
    records: dict[str, Any] = {}
    for kind, (path, content) in files.items():
        path.write_text(content, encoding="utf-8")
        records[kind] = {"path": path.name, "sha256": hashlib.sha256(content.encode()).hexdigest(), "size_bytes": len(content.encode())}
    contract = [{
        "name": register.name,
        "offset": register.offset,
        "reset": register.reset,
        "fields": [{"name": field.name, "lsb": field.lsb, "width": field.width, "access": field.access, "reset": field.reset} for field in register.fields],
    } for register in spec.registers]
    manifest = {"schema_version": "register-bundle-v1", "spec_digest": spec.digest(), "spec_name": spec.name, "semantic_contract": contract, "artifacts": records}
    manifest["bundle_sha256"] = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (output / "register-bundle-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def verify_register_bundle(spec: RegisterSpec, output_dir: str | Path, manifest: dict[str, Any]) -> list[str]:
    """Validate generated file digests and semantic source binding."""
    errors: list[str] = []
    try:
        spec.validate()
    except ValueError as exc:
        return [str(exc)]
    body = {key: value for key, value in manifest.items() if key != "bundle_sha256"}
    expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if manifest.get("bundle_sha256") != expected:
        errors.append("bundle self-digest does not match")
    if manifest.get("spec_digest") != spec.digest():
        errors.append("register specification digest does not match")
    root = Path(output_dir)
    artifacts = manifest.get("artifacts", {})
    for kind, item in artifacts.items():
        raw_path = item.get("path", "") if isinstance(item, dict) else ""
        candidate = Path(raw_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(f"generated artifact path escapes bundle: {raw_path}")
            continue
        path = root / candidate
        if not path.is_file():
            errors.append(f"missing generated artifact: {item.get('path')}")
            continue
        content = path.read_text(encoding="utf-8")
        if hashlib.sha256(content.encode()).hexdigest() != item.get("sha256"):
            errors.append(f"generated artifact digest mismatch: {item.get('path')}")
        for register in manifest.get("semantic_contract", []):
            name = str(register.get("name", ""))
            offset = int(register.get("offset", -1))
            reset = int(register.get("reset", -1))
            if kind == "rtl" and f"{name}" not in content:
                errors.append(f"RTL artifact omits register: {name}")
            if kind == "rtl" and f"{spec.addr_width}'d{offset}" not in content:
                errors.append(f"RTL artifact has wrong address for register: {name}")
            if kind == "rtl" and f"{name} <= {spec.data_width}'h{reset:x};" not in content:
                errors.append(f"RTL artifact has wrong reset for register: {name}")
            if kind == "c_header" and f"{spec.name.upper()}_{name.upper()}_OFFSET" not in content:
                errors.append(f"C header omits register: {name}")
            if kind == "c_header" and f"#define {spec.name.upper()}_{name.upper()}_OFFSET 0x{offset:X}u" not in content:
                errors.append(f"C header has wrong address for register: {name}")
            if kind == "uvm_ral" and f"{name}: offset=0x{int(register.get('offset', -1)):X}" not in content:
                errors.append(f"UVM RAL artifact omits register: {name}")
            if kind == "uvm_ral" and f"{name}: offset=0x{offset:X}, reset=0x{reset:X}" not in content:
                errors.append(f"UVM RAL artifact has wrong reset or address for register: {name}")
            if kind == "scoreboard" and f"expected_{name}" not in content:
                errors.append(f"scoreboard artifact omits register: {name}")
            if kind == "scoreboard" and f"expected_{name} <= {spec.data_width}'h{reset:x};" not in content:
                errors.append(f"scoreboard artifact has wrong reset for register: {name}")
            for field in register.get("fields", []):
                field_name = str(field.get("name", ""))
                lsb = int(field.get("lsb", -1))
                width = int(field.get("width", -1))
                field_reset = int(field.get("reset", -1))
                access = str(field.get("access", ""))
                field_range = str(lsb) if width == 1 else f"{lsb + width - 1}:{lsb}"
                if kind == "rtl" and f"{name}.{field_name}" not in content:
                    errors.append(f"RTL artifact omits field: {name}.{field_name}")
                if kind == "rtl" and f"field {name}.{field_name}[{field_range}] access={access}" not in content:
                    errors.append(f"RTL artifact has wrong field semantics: {name}.{field_name}")
                if kind == "c_header" and f"{spec.name.upper()}_{name.upper()}_{field_name.upper()}_ACCESS_{field.get('access')}" not in content:
                    errors.append(f"C header omits field: {name}.{field_name}")
                if kind == "c_header" and f"#define {spec.name.upper()}_{name.upper()}_{field_name.upper()}_LSB {lsb}u" not in content:
                    errors.append(f"C header has wrong field lsb: {name}.{field_name}")
                if kind == "c_header" and f"#define {spec.name.upper()}_{name.upper()}_{field_name.upper()}_WIDTH {width}u" not in content:
                    errors.append(f"C header has wrong field width: {name}.{field_name}")
                if kind == "c_header" and f"#define {spec.name.upper()}_{name.upper()}_{field_name.upper()}_RESET 0x{field_reset:X}u" not in content:
                    errors.append(f"C header has wrong field reset: {name}.{field_name}")
                if kind == "uvm_ral" and f"{field_name}[" not in content:
                    errors.append(f"UVM RAL artifact omits field: {name}.{field_name}")
                if kind == "uvm_ral" and f"{field_name}[{field_range}] access={access} reset=0x{field_reset:X}" not in content:
                    errors.append(f"UVM RAL artifact has wrong field semantics: {name}.{field_name}")
                if kind == "scoreboard" and field_name not in content:
                    errors.append(f"scoreboard artifact omits field: {name}.{field_name}")
                if kind == "scoreboard" and f"field {name}.{field_name}[{field_range}] access={access}" not in content:
                    errors.append(f"scoreboard artifact has wrong field semantics: {name}.{field_name}")
    return errors
