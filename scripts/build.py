"""Validate and compile the two public exception lists with the official sing-box CLI."""
import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"domain", "domain_suffix"}
LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")

def domain(value):
    if not isinstance(value, str) or value != value.strip():
        raise ValueError("invalid domain")
    try:
        normalized = value.rstrip(".").encode("idna").decode("ascii").lower()
    except UnicodeError:
        raise ValueError("invalid domain") from None
    if len(normalized) > 253 or "." not in normalized or any(not LABEL.fullmatch(p) for p in normalized.split(".")):
        raise ValueError("invalid domain")
    if value != normalized:
        raise ValueError("use lowercase ASCII/punycode domains without a trailing dot")
    return normalized

def load(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"version", "rules"} or type(data["version"]) is not int or data["version"] != 5 or not isinstance(data["rules"], list):
        raise ValueError("expected version 5 domain rules")
    result = {field: set() for field in FIELDS}
    for rule in data["rules"]:
        if not isinstance(rule, dict) or not rule or not set(rule) <= FIELDS:
            raise ValueError("only domain and domain_suffix are supported")
        for field, values in rule.items():
            if not isinstance(values, list):
                raise ValueError("expected a domain array")
            for value in values:
                normalized = domain(value)
                if normalized in result[field]:
                    raise ValueError("duplicate domain")
                result[field].add(normalized)
    return result

def within(name, suffix):
    return name == suffix or name.endswith("." + suffix)

def validate(root=ROOT):
    proxy, direct = (load(root / (name + ".json")) for name in ("proxy", "direct"))
    conflict = bool(proxy["domain"] & direct["domain"])
    conflict |= any(within(a, b) or within(b, a) for a in proxy["domain_suffix"] for b in direct["domain_suffix"])
    conflict |= any(within(a, b) for a in proxy["domain"] for b in direct["domain_suffix"])
    conflict |= any(within(a, b) for a in direct["domain"] for b in proxy["domain_suffix"])
    if conflict:
        raise ValueError("proxy/direct overlap")

def build(binary, root=ROOT):
    validate(root)
    # Validate and compile both before touching either published artifact.
    with tempfile.TemporaryDirectory(dir=root, prefix=".srs-") as directory:
        temporary = Path(directory)
        for name in ("proxy", "direct"):
            target = temporary / (name + ".srs")
            subprocess.run([str(binary), "rule-set", "compile", "--output", str(target), str(root / (name + ".json"))], check=True)
            if not target.read_bytes().startswith(b"SRS"):
                raise ValueError("invalid compiled output")
        for name in ("proxy", "direct"):
            target, output = temporary / (name + ".srs"), root / (name + ".srs")
            if not output.exists() or output.read_bytes() != target.read_bytes():
                os.replace(target, output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--sing-box", default="sing-box")
    args = parser.parse_args()
    try:
        validate() if args.check else build(args.sing_box)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Rule build failed: {error}") from None
    print("Exception rule sources: OK" if args.check else "Both SRS artifacts: OK")
