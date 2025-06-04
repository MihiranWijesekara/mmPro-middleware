pipeline {
    agent any

    environment {
        IMAGE_NAME = "mmpro-middleware"
        DOCKER_REGISTRY = "https://hub.docker.com/repositories/achinthamihiran"
        REGISTRY_CREDENTIALS = "dockerhub-creds"
        IMAGE_TAG = "latest"
        USERNAME = "achinthamihiran"
        // Full image name including registry and username
        FULL_IMAGE_NAME = "${USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
        DOCKER_HUB_REPO = 'achinthamihiran/mmpro-middleware'
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
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:latest")
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
                    bat "docker run -d -p 5000:5000 --name ${IMAGE_NAME} ${IMAGE_NAME}"
                }
            }
        }

        stage('Push Docker Image to Registry') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', '${REGISTRY_CREDENTIALS}') {
                        dockerImage.push('latest')
                        echo "Docker image pushed to ${FULL_IMAGE_NAME}"
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