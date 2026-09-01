#!/usr/bin/env node
/** Quality ratchet script for eslint - only fails on NEW errors not in baseline. */

const fs = require('fs');

function normalizePath(path) {
    const normalized = path.replace(/\\/g, '/');
    for (const marker of ['apps/api/', 'apps/web/']) {
        const index = normalized.indexOf(marker);
        if (index >= 0) return normalized.slice(index);
    }
    return normalized;
}

function fingerprints(reports) {
    return reports.flatMap(report => report.messages.map(message => JSON.stringify({
        filePath: normalizePath(report.filePath || report.filename || ''),
        ruleId: message.ruleId,
        severity: message.severity,
        message: message.message,
        line: message.line,
        column: message.column,
    })));
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
        baseline = new Set(fingerprints(JSON.parse(fs.readFileSync(baselinePath, 'utf8'))));
        console.log(`Baseline entries: ${baseline.size}`);
    }

    if (!fs.existsSync(currentPath)) {
        console.log("✓ No eslint output file found");
        return;
    }

    const current = fingerprints(JSON.parse(fs.readFileSync(currentPath, 'utf8')));

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
