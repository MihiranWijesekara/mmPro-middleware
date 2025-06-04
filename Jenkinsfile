pipeline {
    agent any

    environment {
        IMAGE_NAME = "mmpro-middleware"
        DOCKER_REGISTRY = "docker.io"
        REGISTRY_CREDENTIALS = "dockerhub-creds"
        IMAGE_TAG = "latest"
        USERNAME = "achinthamihiran"
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
                        docker stop ${IMAGE_NAME}
                        docker rm ${IMAGE_NAME}
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
                    // Login to Docker registry using Jenkins credentials
                    docker.withRegistry("https://${DOCKER_REGISTRY}", "${REGISTRY_CREDENTIALS}") {
                        // Tag the image with the correct format
                        def image = docker.image("${IMAGE_NAME}")
                        image.tag("${USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}")
                        
                        // Push the tagged image to Docker Hub
                        image.push()
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
