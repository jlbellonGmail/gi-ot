[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$WorktreePath,[switch]$Retry)
$ErrorActionPreference='Stop'
$resolved=[IO.Path]::GetFullPath($WorktreePath)
$registered=@(git worktree list --porcelain)|Where-Object{$_ -eq "worktree $resolved"}
if($registered){throw 'Cleanup bloqueado: el worktree sigue registrado.'}
if(Test-Path -LiteralPath $resolved){$items=@(Get-ChildItem -LiteralPath $resolved -Force);if($items.Count -gt 0){throw 'Cleanup bloqueado: existe contenido residual ambiguo.'}}
git worktree prune
Write-Output 'cleanup: SAFE_NOOP'
