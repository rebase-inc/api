export APP_SETTINGS="rebase.common.config.DevelopmentConfig"
export DATABASE_URL="postgresql://localhost/rebase_web"
export TEST_URL="postgresql://localhost/rebase_test"
export CONNECTION_POOL_SIZE_PER_WORKER=1
if [ ${GITHUB_CLIENT_ID:?} && ${GITHUB_CLIENT_SECRET:?} ]
then

while true; do
    read -p "Please enter your github client id" client_id
    case $client_id in
        [Yy]* ) make install; break;;
    [Nn]* ) exit;;
* ) echo "Please answer yes or no.";;
    esac
done
