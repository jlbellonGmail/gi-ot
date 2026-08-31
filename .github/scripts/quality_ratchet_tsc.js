#!/usr/bin/env node
/** Quality ratchet script for tsc - only fails on NEW errors not in baseline. */

const fs = require('fs');

function main() {
    const baselinePath = "tsc_baseline.txt";
    const currentPath = "tsc_current.txt";

    let baseline;
    if (!fs.existsSync(baselinePath)) {
        console.log("⚠ No baseline found, creating empty baseline");
        baseline = new Set();
    } else {
        console.log(`Loading baseline from ${baselinePath} (size: ${fs.statSync(baselinePath).size} bytes)`);
        baseline = new Set(fs.readFileSync(baselinePath, 'utf8').split('\n').filter(l => l.trim()));
        console.log(`Baseline entries: ${baseline.size}`);
    }

    if (!fs.existsSync(currentPath)) {
        console.log("✓ No tsc output file found");
        return;
    }

    const current = fs.readFileSync(currentPath, 'utf8')
        .split('\n')
        .filter(l => l.includes('error TS'));

    console.log(`Current errors: ${current.length}`);

    const newErrors = current.filter(e => !baseline.has(e.trim()));

    if (newErrors.length > 0) {
        console.error(`::error::Found ${newErrors.length} NEW tsc errors not in baseline:`);
        newErrors.slice(0, 20).forEach(e => console.error('  ' + e));
        if (newErrors.length > 20) {
            console.error(`  ... and ${newErrors.length - 20} more`);
        }
        if (baseline.size > 0) {
            console.error(`DEBUG: First baseline entry: ${next(baseline.values())}`);
        }
        if (current.length > 0) {
            console.error(`DEBUG: First current entry: ${current[0]}`);
        }
        process.exit(1);
    } else {
        console.log("✓ No new tsc errors (quality ratchet passed)");
        const baselineSize = fs.existsSync(baselinePath) ? fs.readFileSync(baselinePath, 'utf8').split('\n').filter(l => l.trim()).length : 0;
        console.log(`  Total current errors: ${current.length} (baseline: ${baselineSize})`);
    }
}

main();