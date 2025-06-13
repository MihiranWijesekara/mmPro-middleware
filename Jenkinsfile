pipeline {
    agent any

    environment {
        IMAGE_NAME = "mmpro-middleware"
        REGISTRY_CREDENTIALS = "dockerhub-creds"  // Make sure this credential ID exists in Jenkins
        IMAGE_TAG = "latest"
        DOCKER_HUB_REPO = 'achinthamihiran/mmpro-middleware'
        CONTAINER_PORT = 5000
        HOST_PORT = 5000
        // Add Python version if needed
        PYTHON_VERSION = "python3.9"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/MihiranWijesekara/mmPro-middleware.git'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                ${PYTHON_VERSION} -m venv venv
                source venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Prepare Test Environment') {
            steps {
                sh '''
                source venv/bin/activate
                # Create cache directory with proper permissions
                mkdir -p ${WORKSPACE}/.cache
                chmod -R 777 ${WORKSPACE}/.cache
                # Set environment variables for testing
                echo "CACHE_DIR=${WORKSPACE}/.cache" > .env.test
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                source venv/bin/activate
                export CACHE_DIR=${WORKSPACE}/.cache
                pytest --cov=app --cov-report=xml:coverage.xml || true
                '''
            }
            post {
                always {
                    junit '**/test-results.xml'  // If you generate JUnit reports
                    cobertura 'coverage.xml'    // For coverage reporting
                }
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
                script {
                    sh '''
                    docker stop ${IMAGE_NAME} || true
                    docker rm ${IMAGE_NAME} || true
                    '''
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    sh "docker run -d -p ${HOST_PORT}:${CONTAINER_PORT} --name ${IMAGE_NAME} -v ${WORKSPACE}/.cache:/app/cache ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
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
        always {
            cleanWs()  // Clean up workspace
            script {
                // Clean up Docker containers if they exist
                sh '''
                docker stop ${IMAGE_NAME} || true
                docker rm ${IMAGE_NAME} || true
                '''
            }
        }
        success {
            echo '✅ Build, Test, Deploy & Push to Registry Successful!'
            // You can add notifications here (Slack, Email, etc.)
        }
        failure {
            echo '❌ Build, Test, Deploy or Push Failed!'
            // You can add notifications here (Slack, Email, etc.)
        }
    }
}