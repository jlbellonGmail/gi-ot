[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$RunDir,
    [switch]$Json
)
$ErrorActionPreference='Stop'
if(!(Test-Path -LiteralPath $RunDir -PathType Container)){throw "No existe run: $RunDir"}
$summary=Join-Path $RunDir 'SUMMARY.md'; $sdd=Join-Path $RunDir 'sdd.json'
if(!(Test-Path $summary -PathType Leaf)){throw 'SUMMARY.md es obligatorio para toda unidad v2.'}
if(!(Test-Path $sdd -PathType Leaf)){throw 'sdd.json es obligatorio para toda unidad v2.'}
$manifest=Get-Content $sdd -Raw|ConvertFrom-Json
if($manifest.profile -notin @('LIGHT','STANDARD','FULL')){throw 'Perfil SDD invalido.'}
$missing=@($manifest.requiredEvidence|Where-Object{!(Test-Path (Join-Path $RunDir $_) -PathType Leaf)})
$result=[ordered]@{valid=($missing.Count -eq 0);profile=$manifest.profile;missing=$missing;run=(Resolve-Path $RunDir).Path}
if($Json){$result|ConvertTo-Json -Depth 8}else{if(!$result.valid){throw "Evidencia faltante: $($missing -join ', ')"};'feature-contract: PASS'}
if(!$result.valid){exit 2}
