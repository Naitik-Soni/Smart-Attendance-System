param(
  [string]$MainBaseUrl = "http://localhost:8000",
  [string]$FaceBaseUrl = "http://localhost:8001",
  [string]$AdminUser = "admin1",
  [string]$AdminPassword = "StrongPass123"
)

$loginBody = @{
  user_id = $AdminUser
  password = $AdminPassword
} | ConvertTo-Json

$login = Invoke-RestMethod -Method Post -Uri "$MainBaseUrl/v1/auth/login" -ContentType "application/json" -Body $loginBody
$token = $login.data.tokens.access_token
$headers = @{ Authorization = "Bearer $token" }

Invoke-RestMethod -Method Post -Uri "$FaceBaseUrl/faces/retention/purge"
Invoke-RestMethod -Method Post -Uri "$MainBaseUrl/v1/admin/retention/cleanup" -Headers $headers

Write-Host "Retention jobs completed."
