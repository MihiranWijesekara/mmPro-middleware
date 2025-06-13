pipeline {
    agent any

    environment {
        IMAGE_NAME = "mmpro-middleware"
        REGISTRY_CREDENTIALS = "dockerhub-creds"  // Jenkins Docker Hub credentials ID
        IMAGE_TAG = "latest"
        DOCKER_HUB_REPO = 'achinthamihiran/mmpro-middleware'
        CONTAINER_PORT = 5000
        HOST_PORT = 5000
        CACHE_DIR = "${WORKSPACE}/.cache"  // Diskcache writable directory
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/MihiranWijesekara/mmPro-middleware.git'
            }
        }

        stage('Install Dependencies & Run Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt

                    export CACHE_DIR=$WORKSPACE/.cache
                    mkdir -p $CACHE_DIR

                    pytest
                '''
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
                        sh """
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
                    sh "docker run -d -p ${HOST_PORT}:${CONTAINER_PORT} --name ${IMAGE_NAME} ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
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
            echo '✅ Build, Test, Dockerize & Push Successful!'
        }
        failure {
            echo '❌ Build, Test or Docker Push Failed!'
        }
    }
}
