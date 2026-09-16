[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Slug,
    [ValidateSet('LIGHT','STANDARD','FULL')][string]$RequestedDepth='',
    [string]$OutputPath=''
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'workunit-lib.ps1')
Assert-SafeSlug $Slug
$root=Get-RepositoryRoot
$tracked=@(git ls-files)
$signals=New-Object System.Collections.Generic.List[string]
foreach($p in $tracked){
    if($p -match '(^|/)(alembic|migrations|\.github|\.agentic|\.audit|scripts)(/|$)'){[void]$signals.Add($p)}
}
$depth=if($RequestedDepth){$RequestedDepth}elseif($signals.Count -gt 8){'STANDARD'}else{'LIGHT'}
$result=[ordered]@{assessment='ASSESS'; deterministic=$true; slug=$Slug; depth=$depth; signals=@($signals | Select-Object -First 25); rationale='La profundidad se determina por señales de riesgo y puede ser elevada explícitamente; nunca se reduce automáticamente.'; generatedAtUtc=[DateTime]::UtcNow.ToString('o')}
$json=$result|ConvertTo-Json -Depth 8
if(!$OutputPath){$OutputPath=Join-Path (Get-WorkUnitRunDir -Slug $Slug) 'assess.jsonl'}
$parent=Split-Path -Parent $OutputPath; New-Item -ItemType Directory -Force -Path $parent|Out-Null
[IO.File]::WriteAllText($OutputPath,$json+[Environment]::NewLine,(New-Object Text.UTF8Encoding($false)))
Write-Output $json
