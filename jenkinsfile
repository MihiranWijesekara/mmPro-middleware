pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        PYTHON = "python"   // or python3 depending on your system
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/MihiranWijesekara/mmPro-middleware.git'
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                bat """
                    ${PYTHON} -m venv ${VENV_DIR}
                    call ${VENV_DIR}\\Scripts\\activate
                    ${PYTHON} -m pip install --upgrade pip
                    ${PYTHON} -m pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                bat """
                    call ${VENV_DIR}\\Scripts\\activate
                    pytest
                """
            }
        }
    }

    post {
        success {
            echo '✅ Build & Test Succeeded!'
        }
        failure {
            echo '❌ Build Failed!'
        }
    }
}
