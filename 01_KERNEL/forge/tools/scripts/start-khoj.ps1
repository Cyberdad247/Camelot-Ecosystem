# Khoj Startup Script
Write-Host "🧠 Starting Khoj AI - Your Second Brain..." -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Start Khoj services
Write-Host "🚀 Starting Khoj services..." -ForegroundColor Yellow
docker compose -f khoj-docker-compose.yml up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
$status = docker compose -f khoj-docker-compose.yml ps --format json | ConvertFrom-Json
$running = $status | Where-Object { $_.State -eq "running" }

if ($running.Count -eq 2) {
    Write-Host ""
    Write-Host "🎉 Khoj is now running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Service Information:" -ForegroundColor Cyan
    Write-Host "  • Khoj Web Interface: http://localhost:42110" -ForegroundColor White
    Write-Host "  • Admin Panel: http://localhost:42110/server/admin" -ForegroundColor White
    Write-Host "  • Database: PostgreSQL on localhost:5432" -ForegroundColor White
    Write-Host ""
    Write-Host "🔑 Admin Credentials:" -ForegroundColor Cyan
    Write-Host "  • Email: admin@khoj.dev" -ForegroundColor White
    Write-Host "  • Password: admin123" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 To stop Khoj, run: docker compose -f khoj-docker-compose.yml down" -ForegroundColor Yellow
} else {
    Write-Host "❌ Some services failed to start. Check logs with:" -ForegroundColor Red
    Write-Host "   docker compose -f khoj-docker-compose.yml logs" -ForegroundColor White
}
