#!/usr/bin/env python3
"""Conservative, deterministic Surge -> Shadowrocket network-only compiler.

Upstream files are untrusted DATA. Never execute or import them.
JavaScript, unknown directives and third-party redirects are NOT published.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
from pathlib import Path

ALLOWED_RULES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6"}
ALLOWED_POLICIES = {"REJECT", "REJECT-TINYGIF", "REJECT-DROP"}
ALLOWED_REJECTIONS = {
    "reject", "reject-200", "reject-404", "reject-img", "reject-dict", "reject-array"
}
HOST_RE = re.compile(r"^(?:\*\.)?[a-z0-9][a-z0-9._-]*\.[a-z]{2,}$", re.I)
SENSITIVE_HOSTS = (
    "apple.com", "icloud.com", "itunes.com", "mzstatic.com", "apple-dns.net",
    "bank", "paypal.com", "stripe.com", "alipay.com"
)
SECTIONS = ("Rule", "URL Rewrite", "Map Local", "MITM")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normal_sections(raw: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    active = ""
    for item in raw.splitlines():
        line = item.strip()
        if not line or line.startswith(("#", ";", "//")):
            continue
        if line.startswith("[") and line.endswith("]"):
            active = line[1:-1].strip()
            sections.setdefault(active, [])
            continue
        if active:
            sections.setdefault(active, []).append(line)
    return sections


def valid_host(host: str) -> bool:
    if not HOST_RE.fullmatch(host) or ".." in host:
        return False
    trimmed = host[2:] if host.startswith("*.") else host
    return not any(
        trimmed == bad or trimmed.endswith("." + bad)
        for bad in SENSITIVE_HOSTS
    )


def parse_rules(lines: list[str], rejected: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        fields = [x.strip() for x in line.split(",")]
        if len(fields) < 3:
            rejected.append("invalid rule syntax")
            continue
        kind, value, policy = fields[:3]
        kind, policy = kind.upper(), policy.upper()
        if kind not in ALLOWED_RULES or policy not in ALLOWED_POLICIES:
            rejected.append("unsupported/non-reject rule")
            continue
        if kind in ("IP-CIDR", "IP-CIDR6"):
            try:
                ipaddress.ip_network(value, strict=False)
            except ValueError:
                rejected.append("invalid IP CIDR")
                continue
        elif kind == "DOMAIN-KEYWORD":
            if not re.fullmatch(r"[a-zA-Z0-9._-]{2,120}", value):
                rejected.append("invalid domain keyword")
                continue
        elif not valid_host(value):
            rejected.append("invalid/sensitive domain")
            continue
        out.append(f"{kind}, {value}, {policy}")
    return sorted(set(out))


def parse_rewrites(lines: list[str], rejected: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        pieces = line.split()
        if len(pieces) == 3 and pieces[1] == "-" and pieces[2] in ALLOWED_REJECTIONS:
            # No redirect destinations; only block actions.
            if pieces[0].startswith(("^http", "http")) and len(pieces[0]) < 1500:
                out.append(line)
                continue
        rejected.append("unsupported/non-blocking URL rewrite")
    return sorted(set(out))


def parse_maps(lines: list[str], rejected: list[str]) -> list[str]:
    # Only inert, inline JSON/text placeholders, no external files or code.
    fmt = re.compile(
        r'^(\S+)\s+data-type=(json|text)\s+data="([^"]*)"\s+status-code=(200|204)$'
    )
    out: list[str] = []
    for line in lines:
        m = fmt.fullmatch(line)
        if m and m.group(1).startswith(("^http", "http")) and m.group(3) in ("", "{}", "[]"):
            # Shadowrocket supports text/file/tiny-gif/base64, not Surge json.
            # Keep the harmless inline JSON payload and convert its response type.
            out.append(line.replace("data-type=json", "data-type=text"))
        else:
            rejected.append("unsupported/remote Map Local payload")
    return sorted(set(out))


def parse_mitm(lines: list[str], rejected: list[str]) -> list[str]:
    hosts: set[str] = set()
    for line in lines:
        match = re.fullmatch(r"hostname\s*=\s*(?:%APPEND%\s*)?(.+)", line, re.I)
        if match is None:
            rejected.append("unsupported MITM directive")
            continue
        for host in re.split(r"[,\s]+", match.group(1).strip()):
            if not host:
                continue
            if valid_host(host):
                hosts.add(host)
            else:
                rejected.append("invalid/sensitive MITM hostname")
    # Extremely broad MITM lists should never be activated via aggregate modules.
    if len(hosts) > 100:
        rejected.append("MITM list exceeds 100 hosts; omitted")
        return []
    return sorted(hosts)


def compile_module(source: Path, relative: Path, raw: str) -> tuple[str | None, dict]:
    sections = normal_sections(raw)
    reasons: list[str] = []
    rule = parse_rules(sections.get("Rule", []), reasons)
    rewrite = parse_rewrites(sections.get("URL Rewrite", []), reasons)
    maps = parse_maps(sections.get("Map Local", []), reasons)
    has_scripts = bool(sections.get("Script"))
    unsupported = {key: len(lines) for key, lines in sections.items()
                   if key not in SECTIONS and lines}
    mitm = parse_mitm(sections.get("MITM", []), reasons) if (rewrite or maps) else []
    if not (rule or rewrite or maps):
        return None, {
            "status": "no_supported_network_rules", "scripts_omitted": len(sections.get("Script", [])),
            "unsupported": unsupported, "rejected": reasons,
        }
    name_match = re.search(r"^#!name=(.*)$", raw, re.M)
    name = name_match.group(1).strip() if name_match else relative.stem
    name = name[:110].replace("\r", "").replace("\n", " ")
    output = [
        f"#!name=R-Store | {name}",
        "#!desc=Shadowrocket network-only port; upstream JS deliberately omitted; not device-verified",
        "#!author=zirawell (upstream) & wjx-wp (adaptation)",
        "#!homepage=https://github.com/wjx-wp/R-Store-Shadowrocket",
        f"# upstream: Rule/Surge/Adblock/{relative.as_posix()}",
        "# IMPORTANT: No upstream JavaScript is executed by this module.",
        "# Enable only the App modules you need. Requires HTTPS MITM for URL Rewrite / Map Local.",
        "",
    ]
    for header, content in (("Rule", rule), ("URL Rewrite", rewrite), ("Map Local", maps)):
        if content:
            output += [f"[{header}]", *content, ""]
    if mitm:
        output += ["[MITM]", "hostname = %APPEND% " + ", ".join(mitm), ""]
    counts = {"rules": len(rule), "rewrites": len(rewrite), "maps": len(maps),
              "mitm_hosts": len(mitm), "scripts_omitted": len(sections.get("Script", [])),
              "unsupported": unsupported, "rejected": reasons}
    return "\n".join(output).rstrip() + "\n", counts


def output_path(relative: Path) -> Path:
    parts = relative.parts
    # Upstream separates standalone apps, two kinds of applets, websites and bundles.
    # Preserve every directory so e.g. Applet/Wechat and Applet/Alipay never collide.
    if parts and parts[0] in {"App", "All", "Applet", "Web"}:
        return Path(*parts).with_suffix(".module")
    raise ValueError(f"unexpected source path: {relative}")


def safe_script_hashes(scripts_dir: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not scripts_dir.is_dir():
        raise ValueError(f"scripts source missing: {scripts_dir}")
    for path in sorted(scripts_dir.rglob("*.js")):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"script symlink or invalid source: {path}")
        result[path.relative_to(scripts_dir).as_posix()] = digest(path.read_bytes())
    return result


def validate_output(out: Path) -> dict:
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = list(out.rglob("*.module"))
    if manifest["generated_modules"] != len(files):
        raise ValueError("module count mismatch")
    if len(files) < 25:
        raise ValueError("too few modules generated; refusing catastrophic publish")
    for file in files:
        key = file.relative_to(out).as_posix()
        meta = manifest["modules"].get(key)
        if not meta or meta.get("sha256") != digest(file.read_bytes()):
            raise ValueError(f"module SHA-256 checksum mismatch: {key}")
        if file.is_symlink():
            raise ValueError(f"symlink in output: {file}")
        data = file.read_text(encoding="utf-8")
        if "[Script]" in data or "script-path=" in data or "http_backend" in data:
            raise ValueError(f"executable script in static output: {file}")
        if "hostname =" in data and "hostname = %APPEND% " not in data:
            raise ValueError(f"non-additive MITM: {file}")
        if key.startswith("Lite/") and any(tag in data for tag in ("[MITM]", "[URL Rewrite]", "[Map Local]", "[Script]")):
            raise ValueError(f"Lite module must only have [Rule] directives: {key}")
        allowed = set(SECTIONS)
        for sec in re.findall(r"^\[([^\]]+)\]$", data, re.M):
            if sec not in allowed:
                raise ValueError(f"unknown output directive [{sec}]: {file}")
    if set(manifest["modules"]) != {p.relative_to(out).as_posix() for p in files}:
        raise ValueError("manifest paths do not match output")
    return manifest


def build(source: Path, scripts: Path, out: Path, sha: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("upstream commit SHA must be 40 hex chars")
    if not source.is_dir():
        raise ValueError("missing Surge source directory")
    modules = sorted(source.rglob("*.sgmodule"))
    if len(modules) < 100:
        raise ValueError("upstream source unexpectedly small")
    out.mkdir(parents=True, exist_ok=True)
    info: dict[str, dict] = {}
    skipped: dict[str, dict] = {}
    for path in modules:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"unexpected symlink/source file: {path}")
        relative = path.relative_to(source)
        converted, stats = compile_module(path, relative, path.read_text(encoding="utf-8-sig"))
        dest_rel = output_path(relative).as_posix()
        if converted is None:
            skipped[relative.as_posix()] = stats
            continue
        dest = out / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            raise ValueError(f"duplicate destination: {dest_rel}")
        dest.write_text(converted, encoding="utf-8")
        info[dest_rel] = {"upstream": relative.as_posix(), "sha256": digest(converted.encode()),
                          "variant": "network", **stats}
        # Lite variant adds ONLY inert domain/IP blocking rules: no certificate,
        # response interception, TLS decryption, remote script, or dynamic content.
        lite_rules = normal_sections(converted).get("Rule", [])
        if lite_rules:
            lite_rel = "Lite/" + dest_rel
            lite_dest = out / lite_rel
            lite_dest.parent.mkdir(parents=True, exist_ok=True)
            lite_name = next((line.split("=", 1)[1] for line in converted.splitlines()
                              if line.startswith("#!name=")), relative.stem)
            lite_name = lite_name.replace("R-Store | ", "R-Store Lite | ", 1)
            lite_data = "\n".join([
                f"#!name={lite_name}",
                "#!desc=Domain/IP reject only. No JavaScript, HTTPS decryption, or VPN changes.",
                "#!author=zirawell (upstream) & wjx-wp (adaptation)",
                "#!homepage=https://github.com/wjx-wp/R-Store-Shadowrocket",
                f"# upstream: Rule/Surge/Adblock/{relative.as_posix()}",
                "",
                "[Rule]",
                *lite_rules, "",
            ])
            lite_dest.write_text(lite_data, encoding="utf-8")
            info[lite_rel] = {
                "upstream": relative.as_posix(), "sha256": digest(lite_data.encode()),
                "variant": "lite", "rules": len(lite_rules), "rewrites": 0, "maps": 0,
                "mitm_hosts": 0, "scripts_omitted": stats["scripts_omitted"], "rejected": [],
            }
    manifest = {
        "schema": 1,
        "source_repo": "zirawell/R-Store",
        "source_commit": sha,
        "source_surge_modules": len(modules),
        "generated_modules": len(info),
        "skipped_modules": skipped,
        "scripts_sha256": safe_script_hashes(scripts),
        "modules": info,
        "note": "Network and Lite variants; upstream scripts are never executed or fetched by generated modules",
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    validate_output(out)
    print(f"Generated {len(info)} modules from {len(modules)} input modules; "
          f"{len(skipped)} without safe static rules; {len(manifest['scripts_sha256'])} scripts fingerprinted.")


def mitm_set(content: str) -> set[str]:
    matches = re.findall(r"^\s*hostname\s*=\s*%APPEND%\s*(.*)$", content, re.M | re.I)
    return {h.strip().lower() for item in matches for h in item.split(",") if h.strip()}


def map_set(content: str) -> set[str]:
    section = normal_sections(content).get("Map Local", [])
    return set(section)


def gate(old: Path, new: Path) -> tuple[str, list[str]]:
    new_manifest = validate_output(new)
    if not (old / "manifest.json").exists():
        return "auto", ["first run / initial network-only publication"]
    old_manifest = validate_output(old)
    old_modules = {p.relative_to(old).as_posix(): p for p in old.rglob("*.module")}
    new_modules = {p.relative_to(new).as_posix(): p for p in new.rglob("*.module")}
    reasons: list[str] = []
    if len(new_modules) < len(old_modules) * 0.9:
        raise ValueError("over 10% of published modules disappeared")
    removed = sorted(set(old_modules) - set(new_modules))
    if removed:
        reasons.append(f"deleted existing modules: {len(removed)}")
    added = sorted(set(new_modules) - set(old_modules))
    for path in added:
        data = new_modules[path].read_text(encoding="utf-8")
        if mitm_set(data) or map_set(data):
            reasons.append(f"{path}: newly introduced HTTPS decryption or local response mapping")
    if old_manifest["scripts_sha256"] != new_manifest["scripts_sha256"]:
        reasons.append("upstream JavaScript contents changed: requires human audit")
    for path in sorted(set(old_modules) & set(new_modules)):
        before = old_modules[path].read_text(encoding="utf-8")
        after = new_modules[path].read_text(encoding="utf-8")
        added_hosts = mitm_set(after) - mitm_set(before)
        if added_hosts:
            reasons.append(f"{path}: new HTTPS decrypt hosts: {', '.join(sorted(added_hosts)[:5])}")
        new_maps = map_set(after) - map_set(before)
        if new_maps:
            reasons.append(f"{path}: new response mappings: {len(new_maps)}")
    old_data = {p.relative_to(old).as_posix(): p.read_bytes() for p in old.rglob("*") if p.is_file()}
    new_data = {p.relative_to(new).as_posix(): p.read_bytes() for p in new.rglob("*") if p.is_file()}
    if old_data == new_data:
        return "none", ["up to date"]
    return ("review" if reasons else "auto"), reasons[:40] or ["validated static-only changes"]


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--source", type=Path, required=True)
    build_parser.add_argument("--scripts", type=Path, required=True)
    build_parser.add_argument("--out", type=Path, required=True)
    build_parser.add_argument("--sha", required=True)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("--out", type=Path, required=True)
    gate_parser = commands.add_parser("gate")
    gate_parser.add_argument("--old", type=Path, required=True)
    gate_parser.add_argument("--new", type=Path, required=True)
    gate_parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        build(args.source, args.scripts, args.out, args.sha)
    elif args.command == "check":
        result = validate_output(args.out)
        print(f"Validated {result['generated_modules']} modules")
    else:
        decision, reasons = gate(args.old, args.new)
        print(f"DECISION: {decision}")
        for item in reasons:
            print(" - " + item)
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as stream:
                stream.write("decision=" + decision + "\n")
        (args.new / "decision.txt").write_text(
            decision + "\n" + "\n".join(reasons) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
