[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$AssessmentPath,
    [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference='Stop'
if(!(Test-Path -LiteralPath $AssessmentPath)){throw "No existe ASSESS: $AssessmentPath"}
$assessment=Get-Content -LiteralPath $AssessmentPath -Raw|ConvertFrom-Json
if($assessment.assessment -ne 'ASSESS' -or $assessment.deterministic -ne $true){throw 'ASSESS invalido o no deterministico.'}
if($assessment.depth -notin @('LIGHT','STANDARD','FULL')){throw 'Profundidad SDD invalida.'}
$required=@{LIGHT=@('SUMMARY.md');STANDARD=@('SUMMARY.md','spec.md','plan.md','test-report-1.md');FULL=@('SUMMARY.md','spec.md','plan.md','tasks.md','test-report-1.md','audit-1.md','code-review-1.md')}[$assessment.depth]
$result=[ordered]@{schemaVersion=1;assessmentPath=(Resolve-Path $AssessmentPath).Path;profile=$assessment.depth;requiredEvidence=$required;generatedAtUtc=[DateTime]::UtcNow.ToString('o')}
$parent=Split-Path -Parent $OutputPath; New-Item -ItemType Directory -Force -Path $parent|Out-Null
[IO.File]::WriteAllText($OutputPath,($result|ConvertTo-Json -Depth 8)+[Environment]::NewLine,(New-Object Text.UTF8Encoding($false)))
Write-Output ($result|ConvertTo-Json -Depth 8)
