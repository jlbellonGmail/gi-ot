#!/usr/bin/env node
/** Quality ratchet script for eslint - only fails on NEW errors not in baseline. */

const fs = require('fs');

function normalizePath(path) {
    return path.replace(/\\/g, '/');
}

function normalizeError(error) {
    const normalized = { ...error };
    if (normalized.filename) {
        normalized.filename = normalizePath(normalized.filename);
    }
    return normalized;
}

function main() {
    const baselinePath = "eslint_baseline.json";
    const currentPath = "eslint_current.json";

    let baseline;
    if (!fs.existsSync(baselinePath)) {
        console.log("⚠ No baseline found, creating empty baseline");
        baseline = new Set();
    } else {
        console.log(`Loading baseline from ${baselinePath} (size: ${fs.statSync(baselinePath).size} bytes)`);
        baseline = new Set(JSON.parse(fs.readFileSync(baselinePath, 'utf8')).map(e => JSON.stringify(normalizeError(e))));
        console.log(`Baseline entries: ${baseline.size}`);
    }

    if (!fs.existsSync(currentPath)) {
        console.log("✓ No eslint output file found");
        return;
    }

    const current = JSON.parse(fs.readFileSync(currentPath, 'utf8'))
        .flatMap(r => r.messages)
        .map(e => JSON.stringify(normalizeError(e)));

    console.log(`Current errors: ${current.length}`);

    const newErrors = current.filter(e => !baseline.has(e));

    if (newErrors.length > 0) {
        console.error(`::error::Found ${newErrors.length} NEW eslint errors not in baseline:`);
        newErrors.slice(0, 20).forEach(e => console.error('  ' + e));
        if (newErrors.length > 20) {
            console.error(`  ... and ${newErrors.length - 20} more`);
        }
        process.exit(1);
    } else {
        console.log("✓ No new eslint errors (quality ratchet passed)");
        const baselineSize = fs.existsSync(baselinePath) ? JSON.parse(fs.readFileSync(baselinePath, 'utf8')).length : 0;
        console.log(`  Total current errors: ${current.length} (baseline: ${baseline.size})`);
    }
}

main();