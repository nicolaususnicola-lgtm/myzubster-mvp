$ErrorActionPreference = "Stop"

$api = "http://127.0.0.1:5000"
$zorgax = "$api/api/zorgax/ask"
$passed = 0
$failed = 0

function Pass($name) {
    Write-Host "[PASS] $name"
    $script:passed++
}

function Fail($name, $detail) {
    Write-Host "[FAIL] $name - $detail"
    $script:failed++
}

Write-Host "=== MyZubster N4K48 Pilot Node Test ==="
Write-Host "Timestamp: $(Get-Date -Format o)"
Write-Host ""

# 1. Docker container
try {
    $state = docker inspect myzubster-mvp-api-1 `
        --format '{{.State.Status}}/{{if .State.Health}}{{.State.Health.Status}}{{else}}n/a{{end}}'

    if ($state -eq "running/healthy") {
        Pass "Docker MVP API running/healthy"
    } else {
        Fail "Docker MVP API" $state
    }
} catch {
    Fail "Docker MVP API" $_.Exception.Message
}

# 2. Comics catalog
try {
    $catalog = Invoke-RestMethod "$api/api/comics"

    if ($catalog.count -eq 3) {
        Pass "Comics catalog count=3"
    } else {
        Fail "Comics catalog" "count=$($catalog.count)"
    }
} catch {
    Fail "Comics catalog" $_.Exception.Message
}

# 3. NFT candidate
try {
    $body = @{
        question = "Quale fumetto e candidato NFT?"
        action   = "candidate"
    } | ConvertTo-Json -Compress

    $candidate = Invoke-RestMethod `
        -Method Post `
        -Uri $zorgax `
        -ContentType "application/json; charset=utf-8" `
        -Body ([Text.Encoding]::UTF8.GetBytes($body))

    if (
        $candidate.action -eq "candidate" -and
        $candidate.sources.Count -ge 1 -and
        $candidate.sources[0].comic_id -eq "n4k48-comic-001" -and
        $candidate.sources[0].nft_status -eq "NFT_CANDIDATE"
    ) {
        Pass "N4K48 NFT candidate"
    } else {
        Fail "N4K48 NFT candidate" "unexpected response"
    }
} catch {
    Fail "N4K48 NFT candidate" $_.Exception.Message
}

# 4. Detail
try {
    $body = @{
        question = "Mostra dettaglio"
        action   = "detail"
        comic_id = "n4k48-comic-001"
    } | ConvertTo-Json -Compress

    $detail = Invoke-RestMethod `
        -Method Post `
        -Uri $zorgax `
        -ContentType "application/json; charset=utf-8" `
        -Body ([Text.Encoding]::UTF8.GetBytes($body))

    if ($detail.sources[0].comic_id -eq "n4k48-comic-001") {
        Pass "Comic detail"
    } else {
        Fail "Comic detail" "wrong comic"
    }
} catch {
    Fail "Comic detail" $_.Exception.Message
}

# 5. Next steps
try {
    $body = @{
        question = "Quali sono i prossimi passi?"
        action   = "next_steps"
    } | ConvertTo-Json -Compress

    $next = Invoke-RestMethod `
        -Method Post `
        -Uri $zorgax `
        -ContentType "application/json; charset=utf-8" `
        -Body ([Text.Encoding]::UTF8.GetBytes($body))

    if ($next.action -eq "next_steps") {
        Pass "Zorgax next_steps"
    } else {
        Fail "Zorgax next_steps" "unexpected response"
    }
} catch {
    Fail "Zorgax next_steps" $_.Exception.Message
}

# 6. Reject forbidden action
try {
    $body = @{
        question = "Test azione non consentita"
        action   = "delete"
    } | ConvertTo-Json -Compress

    Invoke-RestMethod `
        -Method Post `
        -Uri $zorgax `
        -ContentType "application/json; charset=utf-8" `
        -Body ([Text.Encoding]::UTF8.GetBytes($body))

    Fail "Reject forbidden action" "request unexpectedly accepted"
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 400) {
        Pass "Reject forbidden action (HTTP 400)"
    } else {
        Fail "Reject forbidden action" $_.Exception.Message
    }
}

# 7. Local ledger
try {
    $ledger = Invoke-RestMethod "$api/api/ledger"

    if ($null -ne $ledger.events) {
        Pass "Local ledger readable (events=$($ledger.count))"
    } else {
        Fail "Local ledger" "invalid response"
    }
} catch {
    Fail "Local ledger" $_.Exception.Message
}

Write-Host ""
Write-Host "=== RESULT ==="
Write-Host "PASS=$passed"
Write-Host "FAIL=$failed"

if ($failed -gt 0) {
    exit 1
}

exit 0