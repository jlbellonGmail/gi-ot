[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$InputPath,[Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference='Stop'
$input=Get-Content $InputPath -Raw|ConvertFrom-Json
if($input.assessment -ne 'ASSESS' -or $input.deterministic -ne $true){throw 'Convergence requiere ASSESS deterministico.'}
$open=@($input.findings|Where-Object{$_.status -eq 'OPEN'})
$result=[ordered]@{schemaVersion=1;assessment=$input.assessment;depth=$input.depth;openCount=$open.Count;findings=@($input.findings);verdict=if($open.Count -eq 0){'CONVERGED'}else{'CHANGES_REQUESTED'};nextAction=if($open.Count -eq 0){'HITL_OR_CLOSE'}else{'BUILDER_RESOLVE_FINDINGS'};iteration=1}
$parent=Split-Path -Parent $OutputPath;New-Item -ItemType Directory -Force -Path $parent|Out-Null
[IO.File]::WriteAllText($OutputPath,($result|ConvertTo-Json -Depth 10)+[Environment]::NewLine,(New-Object Text.UTF8Encoding($false)))
Write-Output ($result|ConvertTo-Json -Depth 10)
