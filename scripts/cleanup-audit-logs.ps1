param(
    [int]$TtlDays = 30
)

Write-Output "Cleanup policy: hard-delete audit logs older than $TtlDays days."
