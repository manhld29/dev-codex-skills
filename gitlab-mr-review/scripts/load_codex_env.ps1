param(
  [string]$EnvFilePath
)

if (-not $EnvFilePath -or [string]::IsNullOrWhiteSpace($EnvFilePath)) {
  $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
  $EnvFilePath = Join-Path $codexHome ".env"
}

if (-not (Test-Path -LiteralPath $EnvFilePath)) {
  Write-Error "Env file not found: $EnvFilePath"
  return
}

Get-Content -LiteralPath $EnvFilePath | ForEach-Object {
  $line = $_.Trim()
  if (-not $line -or $line.StartsWith("#")) {
    return
  }

  if ($line.StartsWith("export ")) {
    $line = $line.Substring(7).Trim()
  }

  $parts = $line -split "=", 2
  if ($parts.Count -ne 2) {
    return
  }

  $key = $parts[0].Trim()
  $value = $parts[1].Trim()

  if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
    $value = $value.Substring(1, $value.Length - 2)
  }

  if ($key) {
    Set-Item -Path ("Env:" + $key) -Value $value
  }
}

Write-Output "Loaded environment variables from $EnvFilePath into current PowerShell session."
