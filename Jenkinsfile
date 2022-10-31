sonar_url = 'https://sonar.morphotech.co.uk'
sonar_analyzed_dir = 'plato_helper_py'
project_name = "plato-helper-py"

pipeline {
    agent {
        label env.agent_label
    }
    stages {
        stage('Build docker') {
            steps {
             sh "docker-compose build"
            }
        }
        stage('Run Tests') {
            steps{
                script{
                    if(!params.get('skipTests', false)) {
                        sh "docker-compose run --rm plato-helper"
                    }
                }
            }
        }
        stage('Sonarqube code inspection') {
            steps {
                script{
                    if(!params.get('skipTests', false)) {
                        sh "docker run --rm -e SONAR_HOST_URL=\"${sonar_url}\" -v \"${WORKSPACE}:/usr/src\"  sonarsource/sonar-scanner-cli:${env.sonarqube_version} -X \
                        -Dsonar.projectKey=${project_name}\
                        -Dsonar.login=${env.sonar_account}\
                        -Dsonar.password=${env.sonar_password}\
                        -Dsonar.python.coverage.reportPaths=coverage/coverage.xml\
                        -Dsonar.projectBaseDir=${sonar_analyzed_dir}\
                        -Dsonar.python.version=3.7,3.8,3.9"
                    }
                }
            }
        }
        stage('Push to PyPi') {
            steps {
                sh "docker-compose run plato-helper-py /bin/bash -c \"poetry config pypi-token.pypi ${pypi_token}; poetry build; poetry publish\""
            }
        }
        stage('Get project version') {
            steps {
                script {
                    project_version = sh(script: 'docker-compose run --rm plato-helper poetry version', returnStdout: true).trim().split(' ')[-1]
                }
                sh "echo 'current project version: ${project_version}'"
            }
        }
        stage ('Dependency Tracker Publisher') {
            steps {
                sh "docker-compose run --rm plato-helper-bom"
                dependencyTrackPublisher artifact: 'bom/bom.xml', projectName: 'plato-helper-py', projectVersion: "${project_version}", synchronous: true
            }
        }
    }
    post {
       cleanup{
           sh "docker-compose down"
       }
   }
}
