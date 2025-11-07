# Buscar e substituir imports
$files = Get-ChildItem -Path "src" -Recurse -Filter "*.py"
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $updated = $content -replace "from k1max", "from printer"
    $updated = $updated -replace "import k1max", "import printer"
    $updated | Set-Content $file.FullName -Encoding utf8
}
Write-Host "Imports atualizados"
