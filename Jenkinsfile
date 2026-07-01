pipeline {
    agent any

    environment {
        IMAGE_NAME = "task-manager-app"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        CONTAINER  = "app-staging"
        APP_PORT   = "5001"
    }

    stages {

        stage('Build') {
            steps {
                echo '=== ETAPA 1: BUILD ==='
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }

stage('Test') {
    steps {
        echo '=== ETAPA 2: TEST ==='
        sh 'mkdir -p test-results && chmod 777 test-results'
        sh """
            docker run --rm \
              --user root \
              -v \$(pwd)/test-results:/app/test-results \
              ${IMAGE_NAME}:${IMAGE_TAG} \
              sh -c "pytest tests/ -v \
                       --junitxml=/app/test-results/results.xml \
                       --no-cov 2>&1 | tee /app/test-results/output.txt"
        """
    }
    post {
        always {
            junit allowEmptyResults: true,
                  testResults: 'test-results/results.xml'
        }
    }
}

        stage('Deploy') {
            steps {
                echo '=== ETAPA 3: DEPLOY ==='
                sh """
                    docker rm -f ${CONTAINER} || true
                    docker run -d \
                      --name ${CONTAINER} \
                      --network jenkins-net \
                      -p ${APP_PORT}:5000 \
                      -e SECRET_KEY=staging-secret-key \
                      ${IMAGE_NAME}:${IMAGE_TAG}
                    echo "App desplegada en http://localhost:${APP_PORT}"
                """
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
        }
        success {
            echo 'Pipeline completado exitosamente.'
        }
        failure {
            echo 'El pipeline falló. Revisar logs.'
        }
    }
}