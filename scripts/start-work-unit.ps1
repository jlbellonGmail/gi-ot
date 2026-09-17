[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Slug,[string]$Version='v2.0.0',[string]$WorktreePath='')
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'workunit-lib.ps1')
Assert-SafeSlug $Slug
Assert-CleanWorktree
if(!$WorktreePath){$WorktreePath=Join-Path (Split-Path -Parent (Get-RepositoryRoot)) (Join-Path 'worktrees' "$Version-$Slug")}
$branch="feature/$Version-$Slug"
if(@(git branch --list $branch).Count -gt 0){throw "La rama ya existe: $branch"}
git worktree add -b $branch $WorktreePath develop
