# Export a .pptx to PDF with the installed Microsoft PowerPoint (COM automation).
# Usage: powershell -ExecutionPolicy Bypass -File export_pdf.ps1 <in.pptx> <out.pdf> [-EmbedFontsTo <out.pptx>]
param(
  [Parameter(Mandatory = $true)][string]$In,
  [Parameter(Mandatory = $true)][string]$Out,
  [string]$EmbedFontsTo = ''
)
$ErrorActionPreference = 'Stop'
$In = (Resolve-Path $In).Path
$Out = [System.IO.Path]::GetFullPath($Out)
$pp = New-Object -ComObject PowerPoint.Application
try {
  # Open(FileName, ReadOnly, Untitled, WithWindow)
  $pres = $pp.Presentations.Open($In, -1, 0, 0)
  # ppSaveAsPDF = 32 (standard / print quality). A lighter digital copy is derived separately.
  $pres.SaveAs($Out, 32)
  Write-Output "PDF: $Out slides=$($pres.Slides.Count) w=$($pres.PageSetup.SlideWidth)pt h=$($pres.PageSetup.SlideHeight)pt"
  if ($EmbedFontsTo) {
    $EmbedFontsTo = [System.IO.Path]::GetFullPath($EmbedFontsTo)
    # SaveAs(FileName, ppSaveAsOpenXMLPresentation=24, EmbedTrueTypeFonts=-1)
    $pres.SaveAs($EmbedFontsTo, 24, -1)
    Write-Output "PPTX (fonts embedded where licensing allows): $EmbedFontsTo"
  }
  $pres.Close()
}
finally {
  $pp.Quit()
  [System.Runtime.Interopservices.Marshal]::ReleaseComObject($pp) | Out-Null
}
