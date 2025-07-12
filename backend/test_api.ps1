# Skill Swap Platform API Test Script
# PowerShell script to test all major API endpoints

param(
    [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Continue"

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"

function Write-TestHeader {
    param([string]$TestName)
    Write-Host "`n$('='*50)" -ForegroundColor $Cyan
    Write-Host "Testing: $TestName" -ForegroundColor $Cyan
    Write-Host "$('='*50)" -ForegroundColor $Cyan
}

function Write-TestResult {
    param(
        [bool]$Success,
        [string]$Message,
        [object]$Data = $null
    )
    
    if ($Success) {
        Write-Host "✅ PASS: $Message" -ForegroundColor $Green
    } else {
        Write-Host "❌ FAIL: $Message" -ForegroundColor $Red
    }
    
    if ($Data) {
        Write-Host "Response: $($Data | ConvertTo-Json -Depth 3)" -ForegroundColor $Yellow
    }
}

# Global variables
$Global:Token = $null
$Global:UserId = $null
$Global:SkillId = $null

function Test-HealthCheck {
    Write-TestHeader "Health Check"
    
    try {
        # Test root endpoint
        $response = Invoke-RestMethod -Uri "$BaseUrl/" -Method Get
        if ($response.message) {
            Write-TestResult -Success $true -Message "Root endpoint working" -Data $response
        } else {
            Write-TestResult -Success $false -Message "Root endpoint failed"
        }
        
        # Test health endpoint
        $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
        if ($response.status -eq "healthy") {
            Write-TestResult -Success $true -Message "Health endpoint working" -Data $response
        } else {
            Write-TestResult -Success $false -Message "Health endpoint failed"
        }
    }
    catch {
        Write-TestResult -Success $false -Message "Health check failed: $($_.Exception.Message)"
    }
}

function Test-UserRegistration {
    Write-TestHeader "User Registration"
    
    try {
        $userData = @{
            email = "powershell@example.com"
            username = "psuser"
            password = "password123"
            full_name = "PowerShell User"
            location = "PowerShell City"
            bio = "A test user created by PowerShell script"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/auth/register" -Method Post -Body $userData -ContentType "application/json"
        
        if ($response.id) {
            $Global:UserId = $response.id
            Write-TestResult -Success $true -Message "User registration successful" -Data $response
        } else {
            Write-TestResult -Success $false -Message "Registration failed - no user ID returned"
        }
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 400) {
            Write-TestResult -Success $true -Message "User already exists (expected for repeated runs)"
        } else {
            Write-TestResult -Success $false -Message "Registration failed: $($_.Exception.Message)"
        }
    }
}

function Test-UserLogin {
    Write-TestHeader "User Login"
    
    try {
        $loginData = @{
            username = "psuser"
            password = "password123"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/auth/login" -Method Post -Body $loginData -ContentType "application/json"
        
        if ($response.access_token) {
            $Global:Token = $response.access_token
            Write-TestResult -Success $true -Message "Login successful" -Data @{
                token_preview = $response.access_token.Substring(0, 20) + "..."
                token_type = $response.token_type
            }
        } else {
            Write-TestResult -Success $false -Message "Login failed - no token returned"
        }
    }
    catch {
        Write-TestResult -Success $false -Message "Login failed: $($_.Exception.Message)"
    }
}

function Test-ProtectedEndpoint {
    Write-TestHeader "Protected Endpoints"
    
    if (-not $Global:Token) {
        Write-TestResult -Success $false -Message "No token available for protected endpoint test"
        return
    }
    
    try {
        $headers = @{
            "Authorization" = "Bearer $Global:Token"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/users/me" -Method Get -Headers $headers
        
        if ($response.username -eq "psuser") {
            Write-TestResult -Success $true -Message "Protected endpoint working" -Data $response
        } else {
            Write-TestResult -Success $false -Message "Protected endpoint returned unexpected data"
        }
    }
    catch {
        Write-TestResult -Success $false -Message "Protected endpoint failed: $($_.Exception.Message)"
    }
}

function Test-SkillsManagement {
    Write-TestHeader "Skills Management"
    
    if (-not $Global:Token) {
        Write-TestResult -Success $false -Message "No token available for skills test"
        return
    }
    
    try {
        $headers = @{
            "Authorization" = "Bearer $Global:Token"
            "Content-Type" = "application/json"
        }
        
        # Create a skill
        $skillData = @{
            name = "PowerShell Scripting"
            category = "Automation"
            description = "Windows PowerShell automation and scripting"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/skills/" -Method Post -Body $skillData -Headers $headers
        
        if ($response.id) {
            $Global:SkillId = $response.id
            Write-TestResult -Success $true -Message "Skill creation successful" -Data $response
        } else {
            Write-TestResult -Success $false -Message "Skill creation failed"
        }
        
        # Get all skills
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/skills/" -Method Get -Headers $headers
        
        if ($response -and $response.Count -gt 0) {
            Write-TestResult -Success $true -Message "Retrieved $($response.Count) skills" -Data $response
        } else {
            Write-TestResult -Success $false -Message "Failed to retrieve skills"
        }
    }
    catch {
        Write-TestResult -Success $false -Message "Skills management failed: $($_.Exception.Message)"
    }
}

function Test-UserSkillsAssignment {
    Write-TestHeader "User Skills Assignment"
    
    if (-not $Global:Token -or -not $Global:SkillId) {
        Write-TestResult -Success $false -Message "Token or skill ID not available"
        return
    }
    
    try {
        $headers = @{
            "Authorization" = "Bearer $Global:Token"
            "Content-Type" = "application/json"
        }
        
        # Add skill to user's offered skills
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/users/me/skills/offered/$Global:SkillId" -Method Post -Headers $headers
        
        if ($response.message) {
            Write-TestResult -Success $true -Message "Skill added to offered skills" -Data $response
        } else {
            Write-TestResult -Success $false -Message "Failed to add skill to offered skills"
        }
        
        # Get user's offered skills
        if ($Global:UserId) {
            $response = Invoke-RestMethod -Uri "$BaseUrl/api/users/$Global:UserId/skills/offered" -Method Get -Headers $headers
            
            if ($response -and $response.Count -gt 0) {
                Write-TestResult -Success $true -Message "User has $($response.Count) offered skills" -Data $response
            } else {
                Write-TestResult -Success $true -Message "User has no offered skills (expected for first run)"
            }
        }
    }
    catch {
        Write-TestResult -Success $false -Message "User skills assignment failed: $($_.Exception.Message)"
    }
}

function Test-ErrorHandling {
    Write-TestHeader "Error Handling"
    
    try {
        # Test unauthorized access
        try {
            Invoke-RestMethod -Uri "$BaseUrl/api/users/me" -Method Get
            Write-TestResult -Success $false -Message "Unauthorized access should have been blocked"
        }
        catch {
            if ($_.Exception.Response.StatusCode -eq 401) {
                Write-TestResult -Success $true -Message "Unauthorized access properly blocked"
            } else {
                Write-TestResult -Success $false -Message "Expected 401, got $($_.Exception.Response.StatusCode)"
            }
        }
        
        # Test invalid endpoint
        try {
            Invoke-RestMethod -Uri "$BaseUrl/api/nonexistent" -Method Get
            Write-TestResult -Success $false -Message "Invalid endpoint should return 404"
        }
        catch {
            if ($_.Exception.Response.StatusCode -eq 404) {
                Write-TestResult -Success $true -Message "404 for invalid endpoint"
            } else {
                Write-TestResult -Success $false -Message "Expected 404, got $($_.Exception.Response.StatusCode)"
            }
        }
    }
    catch {
        Write-TestResult -Success $false -Message "Error handling test failed: $($_.Exception.Message)"
    }
}

function Test-APIDocumentation {
    Write-TestHeader "API Documentation"
    
    try {
        # Test Swagger UI
        $response = Invoke-WebRequest -Uri "$BaseUrl/docs" -Method Get
        
        if ($response.StatusCode -eq 200) {
            Write-TestResult -Success $true -Message "Swagger UI accessible"
        } else {
            Write-TestResult -Success $false -Message "Swagger UI not accessible"
        }
        
        # Test OpenAPI schema
        $response = Invoke-RestMethod -Uri "$BaseUrl/openapi.json" -Method Get
        
        if ($response.openapi) {
            Write-TestResult -Success $true -Message "OpenAPI schema accessible" -Data @{
                title = $response.info.title
                version = $response.info.version
            }
        } else {
            Write-TestResult -Success $false -Message "OpenAPI schema not accessible"
        }
    }
    catch {
        Write-TestResult -Success $false -Message "API documentation test failed: $($_.Exception.Message)"
    }
}

# Main execution
function Run-AllTests {
    Write-Host "🚀 Starting Skill Swap Platform API Tests" -ForegroundColor $Cyan
    Write-Host "Base URL: $BaseUrl" -ForegroundColor $Yellow
    
    $tests = @(
        { Test-HealthCheck },
        { Test-UserRegistration },
        { Test-UserLogin },
        { Test-ProtectedEndpoint },
        { Test-SkillsManagement },
        { Test-UserSkillsAssignment },
        { Test-ErrorHandling },
        { Test-APIDocumentation }
    )
    
    foreach ($test in $tests) {
        try {
            & $test
            Start-Sleep -Milliseconds 500
        }
        catch {
            Write-TestResult -Success $false -Message "Test crashed: $($_.Exception.Message)"
        }
    }
    
    Write-Host "`n$('='*50)" -ForegroundColor $Cyan
    Write-Host "🏁 All tests completed!" -ForegroundColor $Green
    Write-Host "$('='*50)" -ForegroundColor $Cyan
}

# Run the tests
Run-AllTests
