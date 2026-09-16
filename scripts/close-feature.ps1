[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Slug,[switch]$DryRun)
$ErrorActionPreference='Stop'
$roadmap=Join-Path (git rev-parse --show-toplevel).Trim() 'ROADMAP.md'
$content=Get-Content $roadmap -Raw
$matches=[regex]::Matches($content,"(?m)^- \[(?<state>[ x-])\] (?<slug>[^\r\n]+)$")|Where-Object{$_.Groups['slug'].Value -eq $Slug}
if($matches.Count -ne 1){throw "Unidad ambigua o inexistente: $Slug"}
if($matches[0].Groups['state'].Value -ne '-'){throw "La unidad debe estar READY_FOR_PR [-] antes del cierre."}
if(!$DryRun){$content=$content.Replace($matches[0].Value,$matches[0].Value.Replace('-]','x]'));[IO.File]::WriteAllText($roadmap,$content,(New-Object Text.UTF8Encoding($false)))}
Write-Output "close-feature: $Slug $(if($DryRun){'DRY-RUN'}else{'CLOSED'})"
