$ErrorActionPreference='Stop'
$root=(git rev-parse --show-toplevel).Trim();$bad=@(Get-ChildItem (Join-Path $root '.github/workflows') -File -ErrorAction SilentlyContinue|ForEach-Object{Select-String -Path $_.FullName -Pattern 'uses:\s+[^@]+@v\d'})
if($bad.Count){throw 'Workflow action no fijada a SHA.'}
Write-Output 'validate-supply-chain: PASS'
