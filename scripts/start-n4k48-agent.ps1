$ErrorActionPreference = "Stop"

$Image = "myzubster-n4k48-agent:test"
$Container = "n4k48-agent"
$Network = "myzubster-ai-network"
$BridgeUrl = "https://bridge.myzubster.com"
$CatalogApi = "http://api:5000"
$CredentialFile = Join-Path $env:USERPROFILE "N4K48-private\n4k48-node-token.dpapi"
$ExpectedHash = "75ab34d21f668fa48383ac7070c717b074c868694c3042928e4532b5ccd34fa1"

$plain = $null
$protected = $null
$token = $null

try {
    if (-not (Test-Path $CredentialFile)) {
        throw "DPAPI credential not found."
    }

    $existing = docker ps -a --filter "name=^/$Container$" --format '{{.Names}}'
    if ($existing -eq $Container) {
        throw "Container '$Container' already exists."
    }

    Add-Type -AssemblyName System.Security

    $protected = [System.IO.File]::ReadAllBytes($CredentialFile)

    $plain = [System.Security.Cryptography.ProtectedData]::Unprotect(
        $protected,
        $null,
        [System.Security.Cryptography.DataProtectionScope]::CurrentUser
    )

    $token = [System.Text.Encoding]::UTF8.GetString($plain).Trim()

    if ([string]::IsNullOrWhiteSpace($token)) {
        throw "DPAPI credential decrypted to an empty value."
    }

    $env:BRIDGE_URL = $BridgeUrl
    $env:LOCAL_CATALOG_API = $CatalogApi
    $env:BRIDGE_NODE_TOKEN = $token

    docker run -d --rm `
        --name $Container `
        --network $Network `
        -e BRIDGE_URL `
        -e BRIDGE_NODE_TOKEN `
        -e LOCAL_CATALOG_API `
        $Image

    if ($LASTEXITCODE -ne 0) {
        throw "Agent container failed to start."
    }

    $actualHash = docker exec $Container sha256sum /app/agent.py

    if (
        $LASTEXITCODE -ne 0 -or
        $actualHash -notmatch [regex]::Escape($ExpectedHash)
    ) {
        docker stop $Container | Out-Null
        throw "Agent SHA-256 verification FAILED."
    }

    Write-Host "N4K48_AGENT_STARTED"
    Write-Host "AGENT_HASH_OK"
}
finally {
    if ($plain) {
        [Array]::Clear($plain, 0, $plain.Length)
    }

    $token = $null
    $plain = $null
    $protected = $null

    Remove-Item Env:BRIDGE_NODE_TOKEN -ErrorAction SilentlyContinue
    Remove-Item Env:BRIDGE_URL -ErrorAction SilentlyContinue
    Remove-Item Env:LOCAL_CATALOG_API -ErrorAction SilentlyContinue
}
