nexus_url = 'https://nexus.morphotech.co.uk/repository/pypi-hosted/'
sonar_url = 'https://sonar.morphotech.co.uk'
sonar_project_key = 'plato-client'
sonar_analyzed_dir = 'plato_client_py'
docker_image_tag = "plato-client"

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
                        sh "docker-compose run --rm plato-client"
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
        stage('Push to Nexus') {
             steps {
                 sh "docker-compose run plato-client /bin/bash -c \"poetry config repositories.morphotech ${nexus_url}; poetry config http-basic.morphotech ${env.nexus_account} ${env.nexus_password}; poetry build; poetry publish -r morphotech\""
             }
         }
        stage ('Dependency Tracker Publisher') {
            steps {
                sh "python3 create-bom.py"
                dependencyTrackPublisher artifact: 'bom.xml', projectName: 'plato-client', projectVersion: "${docker_image_tag}", synchronous: true
            }
        }
    }
    post {
       cleanup{
           sh "docker-compose down"
       }
   }
}
