# Auto-Sync do Submodule .agents no SessionStart
# Atualiza silenciosamente as Skills e Regras a partir de origin/main caso não haja edições locais pendentes.

$ErrorActionPreference = "SilentlyContinue"

try {
    # Consome stdin enviado pelo Antigravity Hook Runner
    $null = [Console]::In.ReadToEnd()

    $agentsDir = Split-Path -Parent $PSScriptRoot
    if (Test-Path (Join-Path $agentsDir ".git")) {
        Push-Location $agentsDir
        $dirty = git status --porcelain 2>$null
        if ([string]::IsNullOrWhiteSpace($dirty)) {
            git checkout main *>$null
            git pull --ff-only origin main *>$null
        }
        Pop-Location
    }
}
catch {
    # Nunca bloqueia a inicialização da sessão se estiver offline
}

Write-Output '{}'
exit 0
