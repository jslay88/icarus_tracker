def app

pipeline {
    agent any
    environment {
        KUBECONFIG = credentials('jslay-k8s-kubeconfig')
        HOSTNAME = 'icarus-tracker.k8s.jslay.net'
    }
    stages {
        stage('Build API') {
            steps {
                script {
                    sh 'ls -la'
                    apiImage = docker.build("docker.home.jslay.net:5000/jslay/icarus_tracker:${env.BUILD_TAG}",
                    "-f ./backend/container/Dockerfile ./backend")
                }
            }
        }
        /*
        stage('Test') {
            steps {
                script {
                    app.inside {
                        sh 'pip install pytest'
                        sh 'pytest'
                    }
                }
            }
        }
        */
        stage('Push Image') {
            steps{
                script {
                    docker.withRegistry('http://docker.home.jslay.net:5000', 'jenkins-nexus') {
                        apiImage.push()
                    }
                }
            }
        }
        stage('Deploy') {
            when {
                anyOf {
                    branch 'master'
                    // branch 'dev'
                }
            }
            stages {
                stage('k8s Deployment') {
                    steps {
                        script {
                            if (env.BRANCH_NAME != "master") {
                                echo "Setting ${env.BRANCH_NAME} hostname..."
                                HOSTNAME = "${env.BRANCH_NAME}.${env.HOSTNAME}"
                            }
                            echo "Deploying ${env.BRANCH_NAME} to ${HOSTNAME}..."

                            docker.image('alpine/helm:3.5.4').inside("-v $KUBECONFIG:/tmp/kubeconfig -e KUBECONFIG=/tmp/kubeconfig --entrypoint=''") {
                                sh """
                                helm upgrade --install icarus-tracker \
                                --create-namespace --namespace icarus-tracker-${env.BRANCH_NAME} \
                                -f helm/overrides/cluster.yml \
                                --wait helm/icarus-tracker \
                                --set image.tag=${env.BUILD_TAG} \
                                --set ingress.hostName="${HOSTNAME}" \
                                --set ingress.hosts[0].host="${HOSTNAME}" \
                                --set ingress.tls[0].hosts[0]="${HOSTNAME}"
                                """
                            }
                        }
                    }
                }
                stage('Test k8s Deployment') {
                    steps {
                        script {
                            docker.image('alpine/helm:3.5.4').inside("-v $KUBECONFIG:/tmp/kubeconfig -e KUBECONFIG=/tmp/kubeconfig --entrypoint=''") {
                                sh "helm test icarus-tracker --namespace icarus-tracker-${env.BRANCH_NAME}"
                            }
                        }
                    }
                }
            }
        }
    }
}
