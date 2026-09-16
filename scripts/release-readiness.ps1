[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Version,[string]$CandidateBranch='develop')
$ErrorActionPreference='Stop'
if($Version -notmatch '^v\d+\.\d+\.\d+$'){throw 'Version debe usar SemVer con prefijo v.'}
if($CandidateBranch -eq 'main'){throw 'La candidata no puede ser main.'}
$tag=git rev-parse "$Version^{commit}" 2>$null;if($LASTEXITCODE -eq 0){throw "Tag ya existe: $Version"}
$dirty=@(git status --porcelain);if($dirty.Count){throw 'Working tree dirty.'}
Write-Output "release-readiness: PASS (sin publicar $Version)"
