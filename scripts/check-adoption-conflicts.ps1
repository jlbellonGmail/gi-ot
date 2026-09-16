[CmdletBinding()]
param([string]$TargetPath='.')
$ErrorActionPreference='Stop'
$known=@('.agentic','AGENTS.md','ROADMAP.md','.github/workflows/ci.yml','runs','docs/tecnica','apps/api','apps/web')
foreach($p in $known){[pscustomobject]@{path=$p;exists=(Test-Path (Join-Path $TargetPath $p))}}
