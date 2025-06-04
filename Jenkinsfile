pipeline {
    agent any

    environment {
        IMAGE_NAME = "mmpro-middleware"
        REGISTRY_CREDENTIALS = "dockerhub-creds"  // Make sure this credential ID exists in Jenkins
        IMAGE_TAG = "latest"
        DOCKER_HUB_REPO = 'achinthamihiran/mmpro-middleware'
        CONTAINER_PORT = 5000
        HOST_PORT = 5000
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/MihiranWijesekara/mmPro-middleware.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:${IMAGE_TAG}")
                }
            }
        }

        stage('Stop Existing Container') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
                    script {
                        bat """
                        docker stop ${IMAGE_NAME} || echo "Container not running"
                        docker rm ${IMAGE_NAME} || echo "Container not found"
                        """
                    }
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    bat "docker run -d -p ${HOST_PORT}:${CONTAINER_PORT} --name ${IMAGE_NAME} ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
                }
            }
        }

        stage('Push Docker Image to Registry') {
            steps {
                script {
                    docker.withRegistry('', "${REGISTRY_CREDENTIALS}") {
                        dockerImage.push()
                        dockerImage.push("${IMAGE_TAG}")
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✅ Build, Deploy & Push to Registry Successful!'
        }
        failure {
            echo '❌ Build, Deploy or Push Failed!'
        }
    }
}