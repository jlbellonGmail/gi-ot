[CmdletBinding()]
param([string]$RepositoryRoot='')
$ErrorActionPreference='Stop'
if(!$RepositoryRoot){$RepositoryRoot=(git rev-parse --show-toplevel).Trim()}
$dirty=@(git -C $RepositoryRoot status --porcelain)
if($dirty.Count -gt 0){throw 'Working tree dirty.'}
$branch=(git -C $RepositoryRoot branch --show-current).Trim();$head=(git -C $RepositoryRoot rev-parse HEAD).Trim();$origin=(git -C $RepositoryRoot rev-parse origin/develop).Trim()
[pscustomobject]@{valid=($branch -eq 'develop' -or $branch -like 'feature/*');branch=$branch;head=$head;originDevelop=$origin;workingTree='clean'}|ConvertTo-Json
