[CmdletBinding()]
param([switch]$Check)
$ErrorActionPreference='Stop'
$root=(git rev-parse --show-toplevel).Trim();$agents=Get-Content (Join-Path $root '.agentic/agents.json')-Raw|ConvertFrom-Json
$expected=@{
 'CLAUDE.md'=(Get-Content (Join-Path $root 'CLAUDE.md') -Raw)
 'opencode.json'=(ConvertTo-Json ([ordered]@{'$schema'='https://opencode.ai/config.json';instructions=@('AGENTS.md','.claude/rules/*.md');permission=[ordered]@{skill=[ordered]@{'*'='ask';'frontend-design'='deny';'find-skills'='deny'}}}) -Depth 8)
 '.mcp.json'=(Get-Content (Join-Path $root '.agentic/mcp.json')-Raw)
}
foreach($rel in $expected.Keys){$path=Join-Path $root $rel;if($Check){if(!(Test-Path $path)){throw "Adapter drift: $rel"}; if($rel -eq '.mcp.json'){ $a=Get-Content $path -Raw|ConvertFrom-Json; $b=Get-Content (Join-Path $root '.agentic/mcp.json') -Raw|ConvertFrom-Json; if($a.mcpServers.Count -ne $b.servers.Count){throw "Adapter drift: $rel"} } elseif($rel -eq 'opencode.json'){ $a=Get-Content $path -Raw|ConvertFrom-Json; $b=($expected[$rel]|ConvertFrom-Json); if(($a|ConvertTo-Json -Depth 12) -ne ($b|ConvertTo-Json -Depth 12)){throw "Adapter drift: $rel"} } elseif((Get-Content $path -Raw).Trim() -ne ([string]$expected[$rel]).Trim()){throw "Adapter drift: $rel"}}else{throw 'Write mode disabled in this first implementation; use -Check.'}}
Write-Output 'sync-agentic-adapters: PASS'
