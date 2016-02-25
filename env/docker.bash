
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
    eval "$(docker-machine env default)"
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
    docker stop api_scheduler_1 api_web_1 api_rq_default_1 api_cache_1
    _git /api/env/repopulate
    docker start api_cache_1 api_rq_default_1 api_web_1 api_scheduler_1
}

function _log() {
    docker exec -t api_rsyslog_1 tail -f /var/log/rebase.log
}

#
# _create_vm <name>
#
# WARNING: this does not work with VirtualBox and Mac OS X 10.11.3 (Yosemite).
# A CPU count greater than 1 will cause a kernel panic.
#
# It's been reported that it works with VMWare Fusion.
#
function _create_vm() {
    docker-machine create \
        --driver virtualbox \
        --virtualbox-cpu-count "2" \
        --virtualbox-memory "2048" \
        dev
}

