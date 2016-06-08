
export REBASE_HOST="http://dev:3000"

api-use-alpha () {
    export REBASE_HOST="https://alpha.rebaseapp.com"
}

export REBASE_COOKIE_JAR=/tmp/api-cookie-jar.txt

api-curl () {
	curl \
    -s \
	-L \
	-b $REBASE_COOKIE_JAR \
	-c $REBASE_COOKIE_JAR \
	-H "Content-Type: application/json" \
	-X $1 \
	-d "$2" \
	 $REBASE_HOST/api/v1/$3
}

#
## GET something from Rebase
# $ api-get skill_sets
#
api-get () {
	api-curl GET "{}" $1 | jq .
}


#
# DELETE from Rebase
#  api-rm users/3
#
api-rm () {
    api-curl DELETE "" $1
}

#
# POST to rebase
# e.g.:
# api-post "{\"first_name\": \"$1\", \"last_name\":\"$2\", \"email\":\"$3\", \"password\":\"$4\"}" users
#
api-post () {
	curl \
    -s \
	-L \
	-b $REBASE_COOKIE_JAR \
	-c $REBASE_COOKIE_JAR \
	-H "Content-Type: application/json" \
    -H 'Accept: application/json' \
	-X POST \
	--data-binary "$1" \
	 $REBASE_HOST/api/v1/$2
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
# $ api-new-user Joe Blow joe@blow.org foobar
#
api-new-user () {
	api-post \
	"{\"first_name\": \"$1\", \"last_name\":\"$2\", \"email\":\"$3\", \"password\":\"$4\"}" \
	users
}

api-login-raw () {
	api-post \
        "{ \"user\": {\"email\": \"$1\"}, \"password\": \"$2\"}" \
        auth
}

#
# Login to Rebase
# $ api-login you@mail.com password
# 
api-login () {
	export CURRENT_USER=$(api-post "{ \"user\": {\"email\": \"$1\"}, \"password\": \"$2\"}" auth | jq -c '.user') 
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
	api-put \
	"{ \"current_role\": { \"id\": \"$2\"} }" \
	users/$1
}

#
# Create a new SSH public key
# 
# example: api-key "My public key" "$(cat ~/.ssh/id_rsa.pub)"
#
api-key () {
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
api-github-importable-repos() {
    if [ $# -ne 1 ]; then
        echo ""
        echo "Correct syntax:"
        echo "$(tput setaf 2)api-github-importable-repos $(tput setaf 1)<github_account_id>$(tput sgr0)"
        echo ""
        echo "To list your registered Github accounts, run this command:"
        echo "$(tput setaf 2)api-get github_accounts$(tput sgr0)"
        echo "If the return list is empty, go to https://alpha.rebaseapp.com, select your profile,"
        echo "then click on 'Add Github Account'."
        echo "Then, come back here, run 'api-get github_accounts' again and see your account being listed"
        echo ""
        return 1
    fi
    api-get "github_accounts/$1/importable_repos" | jq '.repos[] | .url'
}
