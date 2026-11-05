
$shell = New-Object -ComObject Shell.Application
$rb = $shell.Namespace(0xa)
$items = $rb.Items()
$total = 0
foreach ($item in $items) {
    Write-Output ($item.Name + " | " + $item.Type + " | " + $item.Path)
}
