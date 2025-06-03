pipeline {
    agent any

    environment {
        IMAGE_NAME = "mmpro-middleware"
        DOCKER_REGISTRY = "local"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/MihiranWijesekara/mmPro-middleware.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %IMAGE_NAME% ."
            }
        }

        stage('Stop Existing Container') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
                    bat """
                    docker stop %IMAGE_NAME%
                    docker rm %IMAGE_NAME%
                    """
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                bat "docker run -d -p 5000:5000 --name %IMAGE_NAME% %IMAGE_NAME%"
            }
        }
    }

    post {
        success {
            echo '✅ Build & Deploy Successful!'
        }
        failure {
            echo '❌ Build Failed!'
        }
    }
}
