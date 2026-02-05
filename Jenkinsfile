#!/usr/bin/env groovy

/**
 * Green AI Scanner - Jenkins Pipeline Template
 * 
 * This Jenkinsfile demonstrates how to integrate Green AI scanning
 * into your Jenkins pipeline. It scans your codebase, generates reports,
 * and archives results for trending analysis.
 * 
 * Installation:
 * 1. Create a new Pipeline job in Jenkins
 * 2. Point to this Jenkinsfile in your repository
 * 3. Configure GitHub/GitLab webhook to trigger builds
 */

pipeline {
    agent any
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }
    
    parameters {
        string(name: 'LANGUAGE', defaultValue: 'python', description: 'Code language: python, javascript, etc.')
        choice(name: 'FAIL_ON_CRITICAL', choices: ['true', 'false'], description: 'Fail build on CRITICAL violations?')
    }
    
    environment {
        REPORT_FILE = 'green-ai-report.json'
        ARCHIVE_DIR = "${WORKSPACE}/reports"
        GREEN_AI_VERSION = '0.3.0'
    }
    
    stages {
        stage('Setup') {
            steps {
                script {
                    echo "🌿 Green AI Scanner v${GREEN_AI_VERSION}"
                    echo "📁 Workspace: ${WORKSPACE}"
                    echo "🔧 Language: ${params.LANGUAGE}"
                }
            }
        }
        
        stage('Install Green AI') {
            steps {
                script {
                    try {
                        sh '''
                            python --version
                            pip install --upgrade pip
                            pip install green-ai-agent
                            green-ai --version
                        '''
                    } catch (Exception e) {
                        error "Failed to install Green AI: ${e.message}"
                    }
                }
            }
        }
        
        stage('Scan Codebase') {
            steps {
                script {
                    echo "🔍 Running Green AI scan..."
                    sh '''
                        green-ai scan . --language ${LANGUAGE} --format json > ${REPORT_FILE} || true
                    '''
                }
            }
        }
        
        stage('Analyze Results') {
            steps {
                script {
                    echo "📊 Analyzing scan results..."
                    sh '''
                        python - <<'PYTHON_EOF'
import json
import sys

with open('${REPORT_FILE}', 'r') as f:
    report = json.load(f)

# Count violations by severity
critical = [i for i in report.get('issues', []) if i.get('severity') == 'critical']
high = [i for i in report.get('issues', []) if i.get('severity') == 'high']
medium = [i for i in report.get('issues', []) if i.get('severity') == 'medium']
low = [i for i in report.get('issues', []) if i.get('severity') == 'low']

total = len(report.get('issues', []))

print(f"\\n{'='*50}")
print(f"Green AI Scan Summary")
print(f"{'='*50}")
print(f"🔴 Critical: {len(critical)}")
print(f"🟠 High: {len(high)}")
print(f"🟡 Medium: {len(medium)}")
print(f"🔵 Low: {len(low)}")
print(f"{'='*50}")
print(f"Total Issues: {total}")
print(f"{'='*50}\\n")

# Generate report file for Jenkins
with open('green-ai-summary.txt', 'w') as f:
    f.write(f"CRITICAL={len(critical)}\\n")
    f.write(f"HIGH={len(high)}\\n")
    f.write(f"MEDIUM={len(medium)}\\n")
    f.write(f"LOW={len(low)}\\n")
    f.write(f"TOTAL={total}\\n")

sys.exit(0 if len(critical) == 0 else 1)
PYTHON_EOF
                    '''
                    
                    // Load the summary
                    def summary = readProperties file: 'green-ai-summary.txt'
                    env.CRITICAL_COUNT = summary['CRITICAL']
                    env.HIGH_COUNT = summary['HIGH']
                    env.TOTAL_COUNT = summary['TOTAL']
                }
            }
        }
        
        stage('Publish HTML Report') {
            when {
                expression { fileExists("${REPORT_FILE}") }
            }
            steps {
                script {
                    echo "📄 Publishing HTML report..."
                    sh '''
                        # Create a simple HTML report
                        cat > report.html <<'HTML_EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Green AI Scan Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #0ea5e9; color: white; padding: 20px; border-radius: 8px; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
        .card { padding: 15px; border-radius: 8px; border-left: 4px solid #999; }
        .critical { border-left-color: #ef4444; background: #fee2e2; }
        .high { border-left-color: #f59e0b; background: #fef3c7; }
        .medium { border-left-color: #3b82f6; background: #dbeafe; }
        .low { border-left-color: #10b981; background: #d1fae5; }
        .number { font-size: 28px; font-weight: bold; }
        .label { color: #666; font-size: 12px; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌿 Green AI Scan Report</h1>
        <p>Build: ${BUILD_NUMBER} | ${BUILD_TIMESTAMP}</p>
    </div>
    <div class="summary">
        <div class="card critical">
            <div class="label">🔴 Critical</div>
            <div class="number">${CRITICAL_COUNT}</div>
        </div>
        <div class="card high">
            <div class="label">🟠 High</div>
            <div class="number">${HIGH_COUNT}</div>
        </div>
        <div class="card medium">
            <div class="label">🟡 Medium</div>
            <div class="number">-</div>
        </div>
        <div class="card low">
            <div class="label">🔵 Low</div>
            <div class="number">-</div>
        </div>
    </div>
    <p><small>Report generated by Green AI v${GREEN_AI_VERSION}</small></p>
</body>
</html>
HTML_EOF
                    '''
                }
            }
        }
        
        stage('Archive Results') {
            when {
                expression { fileExists("${REPORT_FILE}") }
            }
            steps {
                script {
                    sh '''
                        mkdir -p ${ARCHIVE_DIR}
                        cp ${REPORT_FILE} ${ARCHIVE_DIR}/report-${BUILD_NUMBER}.json
                        cp report.html ${ARCHIVE_DIR}/report-${BUILD_NUMBER}.html
                    '''
                }
                
                // Archive for Jenkins
                archiveArtifacts artifacts: '**/*report*.json,**/*report*.html',
                                 allowEmptyArchive: true,
                                 fingerprint: true
            }
        }
        
        stage('Mark Build Status') {
            steps {
                script {
                    if (env.CRITICAL_COUNT.toInteger() > 0 && params.FAIL_ON_CRITICAL == 'true') {
                        currentBuild.result = 'UNSTABLE'
                        echo "⚠️ Build marked UNSTABLE: Found ${CRITICAL_COUNT} critical violations"
                    } else {
                        echo "✅ Build status OK"
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Cleanup
            cleanWs(deleteDirs: true, patterns: [[pattern: '.git/**', type: 'INCLUDE']])
        }
        
        success {
            echo "✅ Green AI scan completed successfully"
        }
        
        unstable {
            echo "⚠️ Build unstable due to violations"
        }
        
        failure {
            echo "❌ Green AI scan failed"
        }
    }
}

/**
 * Usage Instructions:
 * 
 * 1. Basic Usage:
 *    - Save this file as 'Jenkinsfile' in your repository root
 *    - Create a new Pipeline job in Jenkins
 *    - Point the job to your Git repository
 *    - Build will automatically scan your code
 * 
 * 2. With Parameters:
 *    - Build with parameters to specify language and fail conditions
 *    - Example: LANGUAGE=python, FAIL_ON_CRITICAL=true
 * 
 * 3. Integration:
 *    - Configure GitHub/GitLab webhooks to trigger builds automatically
 *    - Reports will be archived for trending analysis
 *    - HTML reports available in Jenkins workspace
 * 
 * 4. Credentials:
 *    - No special credentials needed for public Green AI
 *    - Git credentials handled by Jenkins SSH keys
 * 
 * 5. Performance:
 *    - First build will install Green AI (~1-2 minutes)
 *    - Subsequent builds reuse the environment (~30 seconds)
 *    - Full scan time depends on codebase size
 */
