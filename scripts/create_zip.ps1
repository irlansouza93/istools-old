# Script PowerShell para criar o ZIP do plugin istools
# Baseado no Makefile do projeto

$PLUGINNAME = "istools"
$CURRENT_DIR = Get-Location

# Arquivos Python principais
$PY_FILES = @(
    "__init__.py",
    "istools.py", 
    "polygon_generator.py",
    "bounded_polygon_generator.py",
    "extend_lines.py",
    "point_on_surface_generator.py",
    "intersection_line.py",
    "resources.py"
)

# Arquivos de tradução
$TRANSLATION_FILES = @(
    "translations\__init__.py",
    "translations\translate.py", 
    "translations\dictionary.py"
)

# Arquivos extras
$EXTRA_FILES = @(
    "metadata.txt",
    "LICENSE",
    "README.md",
    "README-ENG.md",
    "resources.py"
)

# Diretórios extras
$EXTRA_DIRS = @("i18n", "icons")

Write-Host "Criando ZIP do plugin $PLUGINNAME..."

# Remove ZIP anterior se existir
if (Test-Path "$PLUGINNAME.zip") {
    Remove-Item "$PLUGINNAME.zip" -Force
    Write-Host "ZIP anterior removido."
}

# Cria diretório temporário
$TEMP_DIR = "temp_$PLUGINNAME"
if (Test-Path $TEMP_DIR) {
    Remove-Item $TEMP_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null
New-Item -ItemType Directory -Path "$TEMP_DIR\$PLUGINNAME" | Out-Null

Write-Host "Copiando arquivos Python..."
foreach ($file in $PY_FILES) {
    if (Test-Path $file) {
        Copy-Item $file "$TEMP_DIR\$PLUGINNAME\" -Force
        Write-Host "  Copiado: $file"
    } else {
        Write-Warning "  Arquivo não encontrado: $file"
    }
}

Write-Host "Copiando arquivos de tradução..."
# Cria diretório translations
New-Item -ItemType Directory -Path "$TEMP_DIR\$PLUGINNAME\translations" -Force | Out-Null
foreach ($file in $TRANSLATION_FILES) {
    if (Test-Path $file) {
        Copy-Item $file "$TEMP_DIR\$PLUGINNAME\translations\" -Force
        Write-Host "  Copiado: $file"
    } else {
        Write-Warning "  Arquivo não encontrado: $file"
    }
}

Write-Host "Copiando arquivos extras..."
foreach ($file in $EXTRA_FILES) {
    if (Test-Path $file) {
        Copy-Item $file "$TEMP_DIR\$PLUGINNAME\" -Force
        Write-Host "  Copiado: $file"
    } else {
        Write-Warning "  Arquivo não encontrado: $file"
    }
}

Write-Host "Copiando diretórios extras..."
foreach ($dir in $EXTRA_DIRS) {
    if (Test-Path $dir) {
        Copy-Item $dir "$TEMP_DIR\$PLUGINNAME\" -Recurse -Force
        Write-Host "  Copiado diretório: $dir"
    } else {
        Write-Warning "  Diretório não encontrado: $dir"
    }
}

# Cria o ZIP
Write-Host "Criando arquivo ZIP..."
Compress-Archive -Path "$TEMP_DIR\$PLUGINNAME" -DestinationPath "$PLUGINNAME.zip" -Force

# Remove diretório temporário
Remove-Item $TEMP_DIR -Recurse -Force

Write-Host "ZIP criado com sucesso: $PLUGINNAME.zip"

# Lista o conteúdo do ZIP para verificação
Write-Host "`nConteúdo do ZIP:"
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead("$CURRENT_DIR\$PLUGINNAME.zip")
$zip.Entries | ForEach-Object { Write-Host "  $($_.FullName)" }
$zip.Dispose()