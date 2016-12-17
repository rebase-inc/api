_abspath() {
  echo "$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
}

_prompt() {
  read -e -p "$1 [$2]: " var
  echo ${var:-$2}
}
_buildtype() {
  types="dev pro simple";
  if [[ " $types " =~ " $1 " ]]
  then
    echo $1;
  else
    echo "dev"
  fi
}
_yesnoblock() {
  while true; do
    read -p $1 yn
    case $yn in
      [Yy]* ) return 0; break;;
      [Nn]* ) exit;;
      * ) echo "Please answer yes or no.";;
    esac
  done
}

function _compose() {
  type=`_buildtype $@`
  if [[ $type == $1 ]]; then shift; fi;
  command=$1;
  shift;
  docker-compose -f "layouts/${type}.yml" $command $@;
}

function _build() { _compose build $@; }
function _up() { _compose up $@; }
function _start() { _build $@; _up $@; }
function _stop() { _compose stop $@; }
function _exec() {
  container=$1; shift; docker exec -t $container $@;
}
function _managedb() {
  _exec rest_api /venv/web/bin/python -m rebase.scripts.manage $@;
}

# function _repopulate() {
#   if [ `_buildtype $@` = "pro" ];
#   then
#     _yesnoblock "Wipe out production database and repopulate???";
#   fi;
#   _stop -t 60 ${containers[@]}
#   # if [ "$1" == "--hard" ]; then
#   #     _stop -t 60 rq_git
#   #         _db "dropdb postgres && createdb postgres"
#   #     _start rq_git
#   # fi
#   _git /api/env/repopulate


#    else
#        echo "${bold}Development Mode${off}"
#    fi
#     _compose stop -t 60 ${containers[@]}
#         if [ "$1" == "--hard" ]; then
#             _compose stop -t 60 rq_git
#                 _db "dropdb postgres && createdb postgres"
#             _compose start rq_git
#         fi
#         _git /api/env/repopulate
#     _compose start ${containers[@]}
#     docker-compose -f $COMPOSE_FILE $*
# }

# function _repopulate() {
#   if [[ contains $1 ]]
#   then
#     type = $1
#     shift

#   type=${1:-dev}
#   docker-compose -f "layouts/${type}.yml" stop



#   if
#     _compose stop -t 60 ${containers[@]}
#         if [ "$1" == "--hard" ]; then
#             _compose stop -t 60 rq_git
#                 _db "dropdb postgres && createdb postgres"
#             _compose start rq_git
#         fi
#         _git /api/env/repopulate
#     _compose start ${containers[@]}
#     docker-compose -f $COMPOSE_FILE $*
# }

#
# Repopulate the database.
# With the option '--hard', this will destroy and recreate the database itself.
# Use '--hard' if calling '_repopulate' fails.
# Without option, _repopulate will attempt a 'soft' 'DROP TABLE' .
# Examples:
# $ _repopulate
# $ _repopulate --hard
#
function repopulate() {
   if [ ! -z ${SECRET_KEY+x} ]; then
       declare -a containers=(nginx scheduler web rq_default cache)
       echo "${bold}Production mode${off}"
       echo "Do you wish to wipe out the database and repopulate it?"
       echo "Type ${bold}1${off} or ${bold}2${off} to select your answer"
       select yn in Yes No
       do
           case $yn in
               Yes ) break;;
               No ) return;;
           esac
       done
   else
       echo "${bold}Development Mode${off}"
       declare -a containers=(scheduler rest_api default_queue cache)
   fi
    _compose stop -t 60 ${containers[@]}
        if [ "$1" == "--hard" ]; then
            _compose stop -t 60 rq_git
                _db "dropdb postgres && createdb postgres"
            _compose start rq_git
        fi
        _git /api/env/repopulate
    _compose start ${containers[@]}
    docker-compose -f $COMPOSE_FILE $*
}

usercmd=$1
shift
eval "_$usercmd $@"
