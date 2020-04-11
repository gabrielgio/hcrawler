pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh "docker build -t registry.gitlab.com/gabrielgio/hcrawler:0.0.${env.BUILD_NUMBER} -t registry.gitlab.com/gabrielgio/hcrawler:latest ."
            }
        }
	stage('Push') {
            steps {
                sh "docker push registry.gitlab.com/gabrielgio/hcrawler:0.0.${env.BUILD_NUMBER}"
		        sh "docker push registry.gitlab.com/gabrielgio/hcrawler:latest"
	        }
        }
    }
}
