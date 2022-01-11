def app

pipeline {
    agent any
    environment {
        KUBECONFIG = credentials('jslay-k8s-kubeconfig')
        HOSTNAME = 'free.chaoscreator.k8s.jslay.net'
    }
    stages {
        stage('Build API') {
            steps {
                script {
                    sh 'ls -la'
                    apiImage = docker.build("docker.home.jslay.net:5000/jslay/chaos_creator_free_api:${env.BUILD_TAG}",
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
        stage('Build Bot') {
            steps {
                script {
                    sh 'ls -la'
                    botImage = docker.build("chaos_creator_bot",
                    "-f ./chaos_creator_bot/container/Dockerfile ./chaos_creator_bot")
                }
            }
        }
        stage('Build Frontend') {
            steps {
                script {
                    sh 'ls -la'
                    frontendImage = docker.build("docker.home.jslay.net:5000/jslay/chaos_creator_free_frontend:${env.BUILD_TAG}",
                    "-f ./frontend/container/Dockerfile ./frontend")
                }
            }
        }
        stage('Push Images') {
            steps{
                script {
                    docker.withRegistry('http://docker.home.jslay.net:5000', 'jenkins-nexus') {
                        apiImage.push()
                        frontendImage.push()
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
                            withCredentials([
                              string(
                                credentialsId: 'cc-free-steam-api-key',
                                variable: 'STEAM_API_KEY'
                              ),
                              string(
                                credentialsId: 'cc-free-twitch-client-id',
                                variable: 'TWITCH_CLIENT_ID'
                              ),
                              string(
                                credentialsId: 'cc-free-twitch-client-secret',
                                variable: 'TWITCH_CLIENT_SECRET'
                              )
                            ]) {
                                docker.image('alpine/helm:3.5.4').inside("-v $KUBECONFIG:/tmp/kubeconfig -e KUBECONFIG=/tmp/kubeconfig --entrypoint=''") {
                                    sh """
                                    helm upgrade --install chaos-creator-free \
                                    --create-namespace --namespace chaos-creator-free-${env.BRANCH_NAME} \
                                    -f helm/overrides.yaml \
                                    --wait helm/chaos-creator-free \
                                    --set frontend.image.tag=${env.BUILD_TAG} \
                                    --set api.image.tag=${env.BUILD_TAG} \
                                    --set ingress.enabled=true \
                                    --set ingress.hostName="${HOSTNAME}" \
                                    --set ingress.hosts[0].host="${HOSTNAME}" \
                                    --set ingress.hosts[0].paths[0]="/" \
                                    --set ingress.tls[0].hosts[0]="${HOSTNAME}" \
                                    --set ingress.tls[0].secretName=tls \
                                    --set steam.secret.apiKey="${STEAM_API_KEY}" \
                                    --set twitch.secret.clientId="${TWITCH_CLIENT_ID}" \
                                    --set twitch.secret.clientSecret="${TWITCH_CLIENT_SECRET}"
                                    """
                                }
                            }
                        }
                    }
                }
                stage('Test k8s Deployment') {
                    steps {
                        script {
                            docker.image('alpine/helm:3.5.4').inside("-v $KUBECONFIG:/tmp/kubeconfig -e KUBECONFIG=/tmp/kubeconfig --entrypoint=''") {
                                sh "helm test chaos-creator-free --namespace chaos-creator-free-${env.BRANCH_NAME}"
                            }
                        }
                    }
                }
            }
        }
    }
}
