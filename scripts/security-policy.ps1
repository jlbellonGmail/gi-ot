function Get-SecurityDecision { param([Parameter(Mandatory=$true)][string]$Capability)
 $allowed=@('READ','MODIFY_LOCAL');$gated=@('EXECUTE','NETWORK_READ','GIT_WRITE','REMOTE_WRITE')
 if($allowed -contains $Capability){'ALLOW'}elseif($gated -contains $Capability){'GATE'}else{'DENY'}
}
