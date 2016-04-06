
# Launch a bash session inside a running container:
# $ _bash api_web_1
#
function _bash() {
    docker exec -it api_$1_1 bash
}

# Launch a sh session inside a running container:
# $ _sh api_client_1
#
function _sh() {
    docker exec -it api_$1_1 sh
}

# From any bash session, points Docker to a VM
# If no name is provided, 'default' is the choice
#
# $ _vm [<name>]
#
function _vm() {
    if [ -z $1 ]; then
        name=default
    else
        name=$1
    fi
    eval "$(docker-machine env $name)"
    export REBASE_CLIENT_HOST=$(docker-machine ip $name)
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

#
# Execute any bash command as 'postgres' user on database container
# Example:
# $ _db "psql -l"
#
function _db() {
    echo "$1"
    if [ -z "$1" ]; then
        docker exec -it api_database_1 su -l postgres
    else
        docker exec -it api_database_1 su -l postgres -c "$1"
    fi
}

#
# Repopulate the database.
# With the option '--hard', this will destroy and recreate the database itself.
# Use '--hard' if calling '_repopulate' fails.
# Without option, _repopulate will attempt a 'soft' 'DROP TABLE' .
# Examples:
# $ _repopulate
# $ _repopulate --hard
#
function _repopulate() {
    declare -a containers=(scheduler web rq_default cache)
    docker-compose stop ${containers[@]}
    if [ "$1" == "--hard" ]; then
        docker-compose stop rq_git
        _db "dropdb postgres && createdb postgres"
        docker-compose start rq_git
    fi
    _git /api/env/repopulate
    docker-compose start ${containers[@]}
}

#
# _upgrade
# 
# Migrates the DB to the latest revision
#
# Usage:
# $ _upgrade [--production]
#
function _upgrade() {
    if [ "$(basename $PWD)" != "api" ]; then
        echo "Error: you must run this command from the 'api' repo dir"
        return 1
    fi
    layout='-f production-compose.yml'
    if [ "$1" == "--production" ]; then
        layout=
        echo 'Migrating to the latest version of the database in PRODUCTION.'
    else
        echo 'Migrating to the latest version of the database in DEVELOPMENT.'
    fi
    declare -a containers=(scheduler web rq_default cache)
    docker-compose $layout stop ${containers[@]}
    _git /api/env/upgrade_db
    docker-compose $layout start ${containers[@]}
}

function _log() {
    docker exec -t api_rsyslog_1 tail -100 -f /var/log/rebase.log
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
    if [ -z "$1" ]; then
        echo "Missing machine name: $ _create_vm <machine_name>"
    else
        docker-machine create \
            --driver vmwarefusion \
            --vmwarefusion-cpu-count "2" \
            --vmwarefusion-memory-size "2048" \
            $1
    fi
}

#
# to manually set the IP address of a vm.
# Defaults to 'default'.
#
# $ _fix_ip [<machine>]
#
function _fix_ip() {
    if [ -z $1 ]; then
        vm='default'
    else
        vm="$1"
    fi
    echo "ifconfig eth0 192.168.99.100 netmask 255.255.255.0 broadcast 192.168.99.255 up" | docker-machine ssh "$1" sudo tee /var/lib/boot2docker/bootsync.sh > /dev/null
}

# Add your VM's IP to /etc/hosts as 'dev'
function _add_vm_to_hosts() {
    if [ -z "$1" ]; then
        echo "Missing machine name:  _dev_vm <machine_name>"
    else
        sudo sed -i -n  '/192.168.*.* dev/d' /etc/hosts
        echo "$(docker-machine ip $1) dev" | sudo tee -a /etc/hosts
    fi
}

function _gen_certs() {
    test_flag='--test-cert'
    if [ "$1" == "--production" ]; then
        test_flag=
        echo 'Generating real production certificates'
    else
        echo 'Generating test certificates'
    fi

    docker exec -it api_nginx_1 listen 80
    docker run -it -v etc_letsencrypt:/etc/letsencrypt \
        rebase/letsencrypt certonly \
            $test_flag \
            --webroot-path /etc/letsencrypt/webrootauth \
            -c /config/webroot.ini \
            -d alpha.rebaseapp.com
    docker exec -it api_nginx_1 listen 443
}
