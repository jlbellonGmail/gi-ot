[CmdletBinding()]
param([Parameter(Mandatory=$true)][int]$PullRequest,[int]$TimeoutSeconds=900)
$ErrorActionPreference='Stop'
Write-Output "CI wait delegated to GitHub for PR #$PullRequest; timeout=$TimeoutSeconds."
Write-Output 'No merge action is performed by this script.'
