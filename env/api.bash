
. env/colors.bash

export REBASE_DEV='http://dev:3000'
export REBASE_ALPHA='https://alpha.rebaseapp.com'
export REBASE_HOST="$REBASE_DEV"

api-use-alpha () {
    export REBASE_HOST="$REBASE_ALPHA"
}

api-use-dev () {
    export REBASE_HOST="$REBASE_DEV"
}

export REBASE_COOKIE_JAR=/tmp/api-cookie-jar.txt

export API_SILENT_MODE=0

api-set-silent-mode () {
    previous=$API_SILENT_MODE
    export API_SILENT_MODE=$1
    return $previous
}

api-silent () {
    return $(api-set-silent-mode 1)
}

api-verbose () {
    return $(api-set-silent-mode 0)
}

__echo () {
    echo "API_SILENT_MODE=$API_SILENT_MODE"
    if [ $API_SILENT_MODE -ne 1 ]; then
        echo $1
    fi
}

process_errors () {
    response_and_code="$1"
    http_code=$(echo "$response_and_code" | tail -n 1)
    response=$(echo "$response_and_code" | sed '$d')
    if [ $http_code -gt 399 ] && [ $http_code -lt 600 ]; then
        echo "${bold}HTTP Code${off}: $http_code"
        echo "${bold}Message:${off}$response"
        return 1
    else
        echo "$response"
    fi
}

api-curl () {
    process_errors "$( \
        curl \
        -s \
        -w "\n%{http_code}" \
        -L \
        -b $REBASE_COOKIE_JAR \
        -c $REBASE_COOKIE_JAR \
        -H "Content-Type: application/json" \
        -X $1 \
        -d "$2" \
         $REBASE_HOST/api/v1/$3 \
    )"
}

#
## GET something from Rebase
# $ api-get skill_sets
#
api-get () {
	api-curl GET "{}" $1
}


#
# DELETE from Rebase
#  api-rm users/3
#
api-rm () {
    process_errors "$(api-curl DELETE "" $1)"
}


# Silent version of api-post
# Useful for intermediate POST where user msgs interfere with output processing
_api-post () {
    previous=$(api-silent)
    process_errors "$( \
        curl \
        -s \
        -L \
        -w "\n%{http_code}" \
        -b $REBASE_COOKIE_JAR \
        -c $REBASE_COOKIE_JAR \
        -H "Content-Type: application/json" \
        -H 'Accept: application/json' \
        -X POST \
        --data-binary "$1" \
        $REBASE_HOST/api/v1/$2 \
        )"
    export API_SILENT_MODE=$previous_mode
}

#
# POST to rebase
# e.g.:
# api-post "{\"first_name\": \"$1\", \"last_name\":\"$2\", \"email\":\"$3\", \"password\":\"$4\"}" users
#
api-post () {
    process_errors $(_api-post $*)
}

#
# PUT to rebase
# e.g.:
# api-put "{\"first_name\": \"$1\", \"last_name\":\"$2\", \"email\":\"$3\", \"password\":\"$4\"}" users
#
api-put () {
	api-curl PUT "$1" $2
}

#
# Create user in Rebase
# $ api-new-user 'Joe Blow' joe@blow.org foobar
#
api-new-user () {
	api-post \
	"{\"name\": \"$1\", \"email\":\"$2\", \"password\":\"$3\"}" \
	users
}

api-login-raw () {
	_api-post \
        "{ \"user\": {\"email\": \"$1\"}, \"password\": \"$2\"}" \
        auth
}

#
# Login to Rebase
# $ api-login you@mail.com password
# 
api-login () {
    if [ $# -ne 2 ]; then
        echo "Correct syntax:"
        echo "${green}api-login ${red}<email> <password>${off}"
        echo ""
        return 1
    fi
	export CURRENT_USER=$(_api-post "{ \"user\": {\"email\": \"$1\"}, \"password\": \"$2\"}" auth | jq -c '.user') 
    echo $CURRENT_USER | jq .
}

#
## Logout from Rebase
## $ api-logout
##
api-logout () {
	api-get auth
    export CURRENT_USER=
	echo
	echo "Goodbye!"
}

#
# Set the current role for the current user
# $ api-role <user-id> <role-id>
# 
api-role () {
    if [ $# -ne 2 ]; then
        echo ""
        echo "Correct syntax:"
        echo "${green}api-role ${red}<user-id> <role-id>${off}"
        echo
        return 1
    fi
    export CURRENT_USER=$(api-put "{ \"current_role\": { \"id\": \"$2\"} }" users/$1)
    echo $CURRENT_USER | jq .
}

#
# Create a new SSH public key
# 
# example: api-ssh-key "My public key" "$(cat ~/.ssh/id_rsa.pub)"
#
api-ssh-key () {
    if [ $# -ne 2 ]; then
        echo ""
        echo "Correct syntax:"
        echo "${green}api-ssh-key ${red}\"My awesome public key\" \"<pub_key>\"${off}"
        echo
        echo "Example:"
        echo "${green}api-ssh-key \"My public key\" \"\$(cat ~/.ssh/id_rsa.pub)\"${off}"
        echo 
        echo "To list your existing SSH public key, run this command:"
        echo "${green}api-get ssh_keys${off}"
        echo
        echo "If the return list is empty, go to ${blue}$REBASE_HOST${off}, select your profile,"
        echo "then click on ${magenta}'Add SSH key'${off}."
        echo "Then, run '${green}api-get ssh_keys${off}' again and see your new key being listed"
        echo
        return 1
    fi
    if [ -z ${CURRENT_USER+x} ]; then 
        echo "${red}Please login first, using ${green}'api-login'${red}!${off}"
        return 2
    fi
    echo
    echo "${bold}Title${off}: $1"
    echo "${bold}Public Key${off}:"
    echo "$2"
    echo
    api-post \
    "{ \"user\": $CURRENT_USER, \"title\": \"$1\", \"key\": \"$2\" }" \
    ssh_keys
}

api-ticket-comment() {
    api-post \
    "{ \"user\": $CURRENT_USER, \"content\": \"$2\", \"ticket\": { \"id\": $1 } }" \
    comments
}


# api-bid <auction-id> <contractor-id> <snapshot-id> <price>
api-bid() {
    api-post \
    "{ \
        \"bid\": { \
            \"auction\":    { \"id\": $1 }, \
            \"contractor\": { \"id\": $2 }, \
            \"work_offers\": [ \
                { \
                    \"ticket_snapshot\": { \"id\": $3 }, \
                    \"price\": $4, \
                    \"contractor\": { \"id\": $2 } \
                } \
            ] \
        } \
    }" \
    /auctions/$1/bid
}

#
# api-end-auction <auction-id>
#
api-end-auction() {
    api-post "{}" auctions/$1/end
}

api-fail-auction() {
    api-post "{}" auctions/$1/fail
}

api-work-event() {
    api-post \
    "{ \
        \"comment\": \"$2\" \
    }" \
    works/$1/$3
}

api-halt-work() {
    api-work-event $1 "$2" 'halt'
}

api-resolve-work() {
    api-work-event $1 "$2" 'resolve'
}

api-review-work() {
    api-work-event $1 "$2" 'review'
}

#
# api-complete-work <work-id> "<comment>" <rating>
#
api-complete-work() {
    api-post \
    "{ \
        \"comment\": \"$2\", \
        \"rating\": $3
    }" \
    works/$1/complete
}

#
# api-mediate-work <work-id> "<comment>"
#
api-mediate-work() {
    api-work-event $1 "$2" 'mediate'
}

api-hide-nomination() {
    api-put \
    "{ \
        \"hide\": true \
    }" \
    nominations/$1/$2
}

#
# api-nominate <contractor-id> <ticket-set-id> [<auction-id>]
#
api-nominate() {
    if [ $# -gt 3 ] || [ $# -lt 2 ]; then
        echo "Invalid number of arguments.\nCorrect syntax:\n $  api-nominate <contractor-id> <ticket-set-id> [<auction-id>]"
        return 1; 
    fi;
    if [ $# -eq 3 ]; then
        auction="\"auction\": { \"id\": $3 }, "
    else
        auction=
    fi
    api-post \
    "{ \
        \"contractor\": { \"id\": $1 }, \
        \"ticket_set\": { \"id\": $2 }, \
        $auction
     }" \
     nominations
}

#
# api-new-ticket <title> <comment> [<project_id>]
#
api-new-ticket() {
    if [ $# -eq 3 ]; then
        project=", \"project\": { \"id\": $3 }, "
    else
        project=
    fi
    api-post \
    "{ \
        \"title\": \"$1\", \
        \"first_comment\": \"$2\" \
        $project \
    }" \
    internal_tickets
}

#
# api-github-importable-repos <github_account_id>
#
api-github-projects () {
    if [ $# -ne 1 ]; then
        echo
        echo "Correct syntax:"
        echo "${green}api-github-importable-repos ${red}<github_account_id>${off}"
        echo
        echo "To list your registered Github accounts, run this command:"
        echo "${green}api-get github_accounts${off}"
        echo "If the return list is empty, go to $REBASE_HOST, select your profile,"
        echo "then click on 'Add Github Account'."
        echo "Then, come back here, run 'api-get github_accounts' again and see your account being listed"
        echo
        return 1
    fi
    api-get "github_accounts/$1/importable_repos" | jq '.repos[] | { owner:.owner.login, name, id}'
}

api-import-github-project () {
    if [ $# -ne 2 ]; then
        echo
        echo "Correct syntax:"
        echo "${green} api-import-github-project ${red}<github_account_id> <project_id>${off}"
        echo
        echo "To list the projects you can import, run this command:"
        echo "${green}api-github-projects${off}"
        echo "If the return list is empty, go to ${blue}$REBASE_HOST${off}, select your profile,"
        echo "then click on 'Add Github Account'."
        echo "Then, come back here, run 'api-github-projects' again and see your account being listed"
        echo
        return 1
    fi
    echo "Importing Github Project [$2] using Github Account [$1] "
    output=$(api-post "{}" "github_accounts/$1/import/$2")
    if [ $? -eq 0 ]; then
        echo "$output" | jq '.roles[]'
    else
        echo "$output"
    fi
}
