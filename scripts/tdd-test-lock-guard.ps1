# Guardrail Portável de Runtime para a Fase GREEN do TDD (Compatível com Git Submodule)
# Bloqueia edições em arquivos de teste quando o arquivo sentinela `.tdd-green-lock` está ativo no projeto.

$ErrorActionPreference = "Stop"

try {
    $inputJson = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($inputJson)) {
        Write-Output '{"decision":"allow"}'
        exit 0
    }

    $payload = $inputJson | ConvertFrom-Json
    $targetPath = ""

    if ($null -ne $payload.toolCall -and $null -ne $payload.toolCall.args) {
        if ($null -ne $payload.toolCall.args.Path) {
            $targetPath = [string]$payload.toolCall.args.Path
        }
    }

    if ([string]::IsNullOrWhiteSpace($targetPath)) {
        Write-Output '{"decision":"allow"}'
        exit 0
    }

    # Descobre dinamicamente a pasta .agents e a raiz do projeto hospedeiro (portável para qualquer submodule)
    $agentsDir = Split-Path -Parent $PSScriptRoot
    $projectRoot = Split-Path -Parent $agentsDir

    $isLockActive = (Test-Path (Join-Path $projectRoot ".tdd-green-lock")) -or (Test-Path (Join-Path $agentsDir ".tdd-green-lock"))

    if (-not $isLockActive) {
        $normalizedTarget = $targetPath.Replace("/", "\")
        $normalizedRoot = $projectRoot.Replace("/", "\").TrimEnd("\") + "\"
        if ($normalizedTarget.StartsWith($normalizedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            $relative = $normalizedTarget.Substring($normalizedRoot.Length)
            $firstSegment = ($relative -split "\\")[0]
            if (-not [string]::IsNullOrWhiteSpace($firstSegment)) {
                $subProjectLock = Join-Path $projectRoot (Join-Path $firstSegment ".tdd-green-lock")
                if (Test-Path $subProjectLock) {
                    $isLockActive = $true
                }
            }
        }
    }

    if (-not $isLockActive) {
        Write-Output '{"decision":"allow"}'
        exit 0
    }

    # Regex agnóstico de linguagem para identificar arquivos de teste (C#, Java, Python, TS/JS, Go)
    $testPattern = '(?i)(\\|/)(tests?|__tests__|specs?)(\\|/)|(\.(test|spec|e2e|contract)\.[a-z0-9]+$)|(Tests?\.cs$)|(Test\.java$)|(^test_.*\.py$)|(_test\.(py|go)$)'

    if ($targetPath -match $testPattern) {
        $reason = "VIOLACAO DE TDD (FASE GREEN): O arquivo sentinela .tdd-green-lock esta ativo. Agentes Desenvolvedores (Dev Back/Front) sao PROIBIDOS de alterar, excluir ou enfraquecer arquivos de teste escritos pelo Agente QA. Altere apenas o codigo de producao para fazer o teste passar!"
        $response = @{
            decision = "deny"
            reason   = $reason
        } | ConvertTo-Json -Compress
        Write-Output $response
        exit 0
    }

    Write-Output '{"decision":"allow"}'
    exit 0
}
catch {
    Write-Output '{"decision":"allow"}'
    exit 0
}
