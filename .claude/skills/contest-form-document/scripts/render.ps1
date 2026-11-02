# Render .docx to PDF with Microsoft Word (for page count and visual check).
param([string]$Docx)
$full = (Resolve-Path $Docx).Path
$pdf = [System.IO.Path]::ChangeExtension($full, '.pdf')
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
  $doc = $w.Documents.Open($full, $false, $true)
  $doc.ExportAsFixedFormat($pdf, 17)
  $pages = $doc.ComputeStatistics(2)
  $doc.Close($false)
  "pages=$pages pdf=$pdf"
} finally { $w.Quit() }
