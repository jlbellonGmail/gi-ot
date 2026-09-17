[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$RunDir)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'feature-contract.ps1') -RunDir $RunDir
if(@(git status --porcelain).Count){throw 'Working tree dirty.'}
Write-Output 'ready-for-pr: PASS (HITL pendiente)'
