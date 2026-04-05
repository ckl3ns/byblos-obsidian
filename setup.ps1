# setup.ps1 — Inicialização do byblos-obsidian
# Executar UMA VEZ a partir de C:\workspace\byblos-obsidian\
# PS C:\workspace\byblos-obsidian> .\setup.ps1

Write-Host "=== byblos-obsidian :: setup ===" -ForegroundColor Cyan

# 1. Confirmar que estamos no lugar certo
$root = Get-Location
if (-not (Test-Path "$root\setup.ps1")) {
    Write-Error "Execute a partir de C:\workspace\byblos-obsidian\"
    exit 1
}

# 2. Criar estrutura de pastas (seguro — não sobrescreve nada existente)
$dirs = @(
    "vault\wiki\conceitos", "vault\wiki\passagens", "vault\wiki\autores",
    "vault\wiki\obras", "vault\wiki\periodos", "vault\wiki\tradicoes", "vault\wiki\temas",
    "vault\knowledge\cristologia", "vault\knowledge\soteriologia",
    "vault\knowledge\pneumatologia", "vault\knowledge\escatologia",
    "vault\knowledge\hermeneutica", "vault\knowledge\historia-da-interpretacao",
    "vault\indices", "vault\reports\exegeses", "vault\reports\tematicos",
    "vault\reports\lint", "vault\reports\slides",
    "agents\scripts", "agents\prompts", "agents\tests\fixtures",
    "raw", "docs", ".github\workflows", ".github\ISSUE_TEMPLATE"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}
Write-Host "  [OK] Pastas criadas" -ForegroundColor Green

# 3. Mover Bíblia para vault\ (se ainda não foi movida)
$bibliaOld = "Biblia"   # ajuste se o nome da pasta copiada for diferente
$bibliaNew = "vault\Biblia"
if (Test-Path $bibliaOld) {
    if (-not (Test-Path $bibliaNew)) {
        Move-Item $bibliaOld $bibliaNew
        Write-Host "  [OK] Biblia movida para vault\Biblia" -ForegroundColor Green
    } else {
        Write-Host "  [--] vault\Biblia já existe, pulando" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [--] Pasta Biblia não encontrada na raiz (verifique se já está em vault\)" -ForegroundColor Yellow
}

# 4. Copiar arquivos de configuração gerados
$filesToCopy = @(
    @{ Src = "CLAUDE.md";           Dst = "CLAUDE.md" },
    @{ Src = "README.md";           Dst = "README.md" },
    @{ Src = ".gitignore";          Dst = ".gitignore" },
    @{ Src = "LICENSE";             Dst = "LICENSE" },
    @{ Src = "agents\AGENTS.md";    Dst = "agents\AGENTS.md" },
    @{ Src = "agents\INSTRUCTIONS.md"; Dst = "agents\INSTRUCTIONS.md" },
    @{ Src = "agents\ontology.yaml";Dst = "agents\ontology.yaml" },
    @{ Src = "agents\requirements.txt"; Dst = "agents\requirements.txt" },
    @{ Src = "agents\scripts\ntsk_linker.py"; Dst = "agents\scripts\ntsk_linker.py" },
    @{ Src = "vault\indices\INDEX.md"; Dst = "vault\indices\INDEX.md" },
    @{ Src = "vault\knowledge\INDEX.md"; Dst = "vault\knowledge\INDEX.md" },
    @{ Src = "raw\MANIFEST.md";     Dst = "raw\MANIFEST.md" },
    @{ Src = "docs\convencoes.md";  Dst = "docs\convencoes.md" }
)
Write-Host "  [--] Copie manualmente os arquivos gerados pelo assistente para os destinos acima" -ForegroundColor Yellow

# 5. Git init
if (-not (Test-Path ".git")) {
    git init
    Write-Host "  [OK] Git inicializado" -ForegroundColor Green
} else {
    Write-Host "  [--] Git já inicializado" -ForegroundColor Yellow
}

# 6. Primeiro commit
git add .
git status

Write-Host ""
Write-Host "Revise os arquivos acima e confirme com:" -ForegroundColor Cyan
Write-Host '  git commit -m "chore: estrutura inicial do byblos-obsidian"' -ForegroundColor White
Write-Host ""
Write-Host "Depois conecte ao GitHub:" -ForegroundColor Cyan
Write-Host '  git remote add origin https://github.com/SEU_USUARIO/byblos-obsidian.git' -ForegroundColor White
Write-Host '  git branch -M main' -ForegroundColor White
Write-Host '  git push -u origin main' -ForegroundColor White
Write-Host ""
Write-Host "Configure o Obsidian:" -ForegroundColor Cyan
Write-Host '  Open folder as vault → selecionar C:\workspace\byblos-obsidian\vault' -ForegroundColor White
