#!/usr/bin/env node
/*
 * Design Studio — npm entry point.
 *
 *   design-studio doctor              check this machine
 *   design-studio lint index.html     source gates
 *   design-studio verify index.html   render gates
 *   design-studio --stdio             run the MCP server (used by the registry)
 *
 * The implementation is Python (stdlib only). This shim finds python3 and
 * forwards to scripts/ds.py so the package works on any agent that can
 * spawn a process.
 */

"use strict";

const { spawnSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const ROOT = path.resolve(__dirname, "..");
const CLI = path.join(ROOT, "scripts", "ds.py");

function findPython() {
  const candidates = ["python3", "python"];
  for (const name of candidates) {
    const probe = spawnSync(name, ["--version"], { encoding: "utf8" });
    if (probe.status === 0) return name;
  }
  return null;
}

function main() {
  const args = process.argv.slice(2);
  const python = findPython();
  if (!python) {
    process.stderr.write(
      "design-studio: python3 is required but was not found on PATH.\n"
    );
    process.exit(2);
  }
  if (!fs.existsSync(CLI)) {
    process.stderr.write(`design-studio: missing ${CLI}\n`);
    process.exit(2);
  }

  const forwarded = args[0] === "--stdio" ? ["mcp"] : args;
  const res = spawnSync(python, [CLI, ...forwarded], { stdio: "inherit" });
  process.exit(res.status === null ? 1 : res.status);
}

main();
