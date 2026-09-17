[CmdletBinding()]
param([Parameter(Mandatory=$true)][int]$PullRequest)
$ErrorActionPreference='Stop'
throw "HITL required: PR #$PullRequest cannot be merged automatically by this script."
