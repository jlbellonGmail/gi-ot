[CmdletBinding()]
param([string]$RepositoryRoot='')
$ErrorActionPreference='Stop'
if(!$RepositoryRoot){$RepositoryRoot=(git rev-parse --show-toplevel).Trim()}
$branch=(git -C $RepositoryRoot branch --show-current).Trim();$head=(git -C $RepositoryRoot rev-parse HEAD).Trim();$dirty=@(git -C $RepositoryRoot status --porcelain).Count
$out=[ordered]@{branch=$branch;head=$head;workingTree=if($dirty){'dirty'}else{'clean'};worktrees=@(git -C $RepositoryRoot worktree list --porcelain|Where-Object{$_ -match '^worktree '}).Count;generatedAtUtc=[DateTime]::UtcNow.ToString('o')}
$out|ConvertTo-Json -Depth 5
