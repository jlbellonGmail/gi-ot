[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$BaseCommit)
$ErrorActionPreference='Stop'
$head=(git rev-parse HEAD).Trim();$current=(git rev-parse develop).Trim()
[pscustomobject]@{head=$head;base=$BaseCommit;develop=$current;status=if($head -eq $BaseCommit){'ALIGNED'}else{'RECONCILIATION_REQUIRED'};action='NO_AUTOMATIC_MERGE'}|ConvertTo-Json
