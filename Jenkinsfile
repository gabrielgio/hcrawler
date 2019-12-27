pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh "docker build -t gabrielgio/hcrawler:0.0.${env.BUILD_NUMBER} -t gabrielgio/hcrawler:latest ."
            }
        }
	stage('Push') {
            steps {
                sh "docker push gabrielgio/hcrawler:0.0.${env.BUILD_NUMBER}"
		        sh "docker push gabrielgio/hcrawler:latest"
	        }
        }
    }
}