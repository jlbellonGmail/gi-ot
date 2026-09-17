[CmdletBinding()]
param([string]$RepositoryRoot='')
$ErrorActionPreference='Stop'
if(!$RepositoryRoot){$RepositoryRoot=(git rev-parse --show-toplevel).Trim()}
$required=@('AGENTS.md','CONSTITUTION.md','ROADMAP.md','STATUS.md','.agentic/agents.json','.agentic/models.json','.agentic/mcp.json','.agentic/security-policy.json')
$missing=@($required|Where-Object{!(Test-Path (Join-Path $RepositoryRoot $_) -PathType Leaf)})
if($missing.Count){throw "Integrity missing: $($missing -join ', ')"}
foreach($p in @('.agentic/agents.json','.agentic/models.json','.agentic/mcp.json','.agentic/security-policy.json')){Get-Content (Join-Path $RepositoryRoot $p)-Raw|ConvertFrom-Json|Out-Null}
$canonical = @((Get-ChildItem (Join-Path $RepositoryRoot '.agentic/roles') -Filter '*.md' -File | Select-Object -ExpandProperty FullName) + (Join-Path $RepositoryRoot 'CONSTITUTION.md'))
foreach($file in $canonical){
    if((Get-Content $file -Raw) -match '(?i)\b(luna|sol|claude|codex|opencode|kimi|gemini|openai|anthropic)\b'){throw "Proveedor/modelo hardcodeado en contrato canonico: $file"}
}
Write-Output 'check-integrity: PASS'
