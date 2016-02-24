
# Launch a bash session inside a running container:
# $ _bash api_web_1
#
function _bash() {
    docker exec -it api_$1_1 bash
}

# From any bash session, points Docker to the default VM
# $ _vm
#
function _vm() {
    eval "$(docker-machine env dev)"
    env|sort|grep DOCKER
}

function _shell() {
    docker exec -it api_web_1 /venv/api/bin/python manage shell
}

function _super() {
    docker exec -it api_rq_git_1 /venv/super/bin/supervisorctl -c /etc/git/supervisor.conf $*
}

function _git() {
    docker exec -t api_rq_git_1 $*
}

function _repopulate() {
    docker stop api_web_1 api_rq_default_1 api_cache_1
    _git /api/env/repopulate
    docker start api_cache_1 api_rq_default_1 api_web_1 
}

function _log_cache() {
    docker exec -t api_cache_1 tail -f /log/cache.log
}

function _access_log() {
    docker exec -t api_web_1 tail -f /log/access.log
}

function _error_log() {
    docker exec -t api_web_1 tail -f /log/error.log
}

function _log() {
    docker exec -t $1 tail -f /log/rebase_web.log
}

#
# _create_vm <name>
#
function _create_vm() {
    docker-machine create \
        --driver virtualbox \
        --virtualbox-cpu-count "2" \
        --virtualbox-memory "2048" \
        dev
}
