pipeline {
    agent any

    environment {
        IMAGE_NAME = "mmpro-middleware"
        DOCKER_REGISTRY = "docker.io"
        REGISTRY_CREDENTIALS = "dockerhub-creds"
        IMAGE_TAG = "latest"
        USERNAME = "achinthamihiran"
        // Full image name including registry and username
        FULL_IMAGE_NAME = "${USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
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
                    bat "docker build -t ${IMAGE_NAME} ."
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
                    // First tag the image properly
                    bat "docker tag ${IMAGE_NAME} ${FULL_IMAGE_NAME}"
                    
                    // Then push using Docker Pipeline plugin
                    docker.withRegistry("https://${DOCKER_REGISTRY}", "${REGISTRY_CREDENTIALS}") {
                        docker.image(FULL_IMAGE_NAME).push()
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