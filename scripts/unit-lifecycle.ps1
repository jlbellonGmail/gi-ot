[CmdletBinding()]
param([Parameter(Mandatory=$true)][ValidateSet('inspect','reconcile')][string]$Action,[Parameter(Mandatory=$true)][string]$Slug,[string]$Version='v2.0.0')
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'workunit-lib.ps1')
Assert-SafeSlug $Slug
$head=((git rev-parse HEAD) -join "`n").Trim();$base=((git rev-parse develop) -join "`n").Trim()
$result=[ordered]@{action=$Action;slug=$Slug;version=$Version;head=$head;develop=$base;status=if($head -eq $base){'ALIGNED'}else{'DIVERGED'};destructiveAction=$false}
$result|ConvertTo-Json -Depth 6
if($Action -eq 'reconcile' -and $result.status -eq 'DIVERGED'){throw 'Reconcile requiere decisión explícita; no modifica silenciosamente la unidad.'}
