$slides = Get-ChildItem "C:\Users\ABCOM\.gemini\antigravity\playground\crimson-plasma\ppt_extract\ppt\slides\slide*.xml" | Sort-Object { [int]($_.BaseName -replace 'slide','') }
$output = ""
foreach ($slide in $slides) {
    $content = Get-Content $slide.FullName -Raw
    $matches = [regex]::Matches($content, '<a:t(?:.*?)>(.*?)</a:t>')
    $texts = $matches | ForEach-Object { $_.Groups[1].Value }
    $slideText = ($texts -join " ").Trim()
    if ($slideText -ne "") {
        $output += "Slide $($slide.BaseName -replace 'slide',''): $slideText`r`n"
    }
}
$output | Out-File -FilePath "C:\Users\ABCOM\.gemini\antigravity\playground\crimson-plasma\ppt_extract\presentation_text.txt"
