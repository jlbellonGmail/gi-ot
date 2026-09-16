[CmdletBinding()]
param([string]$CatalogPath='')
$ErrorActionPreference='Stop'
if(!$CatalogPath){$CatalogPath=Join-Path (git rev-parse --show-toplevel).Trim() '.agentic/mcp.json'}
$catalog=Get-Content $CatalogPath -Raw|ConvertFrom-Json
if($catalog.schemaVersion -ne 1){throw 'MCP schemaVersion invalido.'}
if(@($catalog.servers.PSObject.Properties).Count -ne 0){throw 'Sólo se permiten servidores MCP explícitamente aprobados.'}
Write-Output 'mcp-catalog: PASS (0 servers)'
