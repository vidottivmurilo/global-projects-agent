# Inicia o Painel Visual da Fábrica de Software Multi-Agente
param(
    [int]$Intervalo = 3,
    [int]$Porta = 7420,
    [switch]$SemNavegador
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AgentsDir = Split-Path -Parent $ScriptDir
$PainelDir = Join-Path $AgentsDir "painel"
$ColetorPy = Join-Path $PainelDir "coletor.py"
$IndexHtml = Join-Path $PainelDir "publico\index.html"

# 1. Verifica Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    $PythonCmd = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $PythonCmd) {
    Write-Error "Python 3 não foi encontrado no PATH. Instale o Python 3.9+ para usar o painel."
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  🚀 Painel de Telemetria da Fábrica de Software" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 2. Executa passada inicial síncrona
Write-Host "[1/3] Gerando dados iniciais da esteira..." -ForegroundColor Gray
& $PythonCmd.Source $ColetorPy --uma-vez

# 3. Inicia o coletor em background
Write-Host "[2/3] Iniciando coletor em segundo plano (atualizando a cada ${Intervalo}s)..." -ForegroundColor Gray
$Job = Start-Job -ScriptBlock {
    param($py, $script, $intervalo, $porta)
    & $py $script --intervalo $intervalo --porta $porta
} -ArgumentList $PythonCmd.Source, $ColetorPy, $Intervalo, $Porta

Write-Host "      Job ID: $($Job.Id) rodando na porta $Porta" -ForegroundColor Green

# 4. Abre o navegador
if (-not $SemNavegador) {
    Write-Host "[3/3] Abrindo painel no navegador..." -ForegroundColor Gray
    Start-Process $IndexHtml
}

Write-Host ""
Write-Host "Painel ativo e pronto! Para parar o coletor:" -ForegroundColor Yellow
Write-Host "  Stop-Job -Id $($Job.Id); Remove-Job -Id $($Job.Id)" -ForegroundColor DarkGray
Write-Host "==========================================================" -ForegroundColor Cyan
