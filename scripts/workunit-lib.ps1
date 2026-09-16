$ErrorActionPreference = 'Stop'

function Get-RepositoryRoot {
    return ((git rev-parse --show-toplevel 2>$null) -join "`n").Trim()
}

function Get-WorkUnitRunDir {
    param([Parameter(Mandatory=$true)][string]$Slug,[string]$Version='v2.0.0')
    Join-Path (Join-Path (Get-RepositoryRoot) 'runs') (Join-Path $Version $Slug)
}

function Assert-SafeSlug {
    param([Parameter(Mandatory=$true)][string]$Slug)
    if ($Slug -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') { throw "Slug invalido: $Slug" }
}

function Get-CurrentBranch { ((git branch --show-current) -join "`n").Trim() }

function Assert-CleanWorktree {
    $dirty = @(git status --porcelain)
    if ($dirty.Count -gt 0) { throw 'Working tree no limpio.' }
}
