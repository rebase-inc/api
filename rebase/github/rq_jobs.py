from datetime import datetime
from functools import lru_cache
from logging import getLogger
from subprocess import check_call, call

from rebase.github.session import make_admin_github_session


logger = getLogger()


_gh_datetime_format = '%Y-%m-%dT%H:%M:%SZ'


@lru_cache(maxsize=None)
def get_or_make_user(session, user_id, user_login):
    '''
    return a User or GithubUser instance for the 'user_id' and 'user_login' provided
    '''
    from rebase.models import GithubAccount, GithubUser
    account = GithubAccount.query.filter(GithubAccount.account_id==user_id).first()
    if not account:
        _user = GithubUser.query.filter(GithubUser.github_id==user_id).first()
        if not _user:
            gh_user = session.api.get('/users/{username}'.format(username=user_login)).data
            _user = GithubUser(user_id, user_login, gh_user['name'])
    else:
        _user = account.user
    return _user


def import_tickets(project_id, account_id):
    session = make_admin_github_session(account_id)
    from rebase.models import (
        GithubProject,
        GithubTicket,
        Comment,
    )
    project = GithubProject.query.get_or_404(project_id)
    if not project:
        return 'Unknow project with id: {}'.format(project_id)
    repo_url = '/repos/{owner}/{repo}'.format(
        owner=project.organization.name,
        repo=project.name
    )
    languages = session.api.get(repo_url+'/languages').data
    # Normalize the language values by dividing by the sum of values.
    # Ultimately we want a level of difficulty per language, not a relative distribution of the quantity of code.
    # But this will do for now.
    total = sum(languages.values())
    languages = { language: code_size/total for language, code_size in languages.items() }
    issues = session.api.get(repo_url+'/issues').data
    tickets = []
    komments = []
    for issue in issues:
        ticket = GithubTicket(project, issue['number'], issue['title'], datetime.strptime(issue['created_at'], _gh_datetime_format))
        ticket.skill_requirement.skills = languages
        tickets.append(ticket)
        issue_user = issue['user']
        if len(issue['body']):
            body = Comment(
                get_or_make_user(
                    session,
                    issue_user['id'],
                    issue_user['login'],
                ),
                issue['body'],
                ticket=ticket
            )
            komments.append(body)
        comments = session.api.get(issue['url']+'/comments').data
        for comment in comments:
            comment_user = comment['user']
            ticket_comment = Comment(
                get_or_make_user(
                    session,
                    comment_user['id'],
                    comment_user['login'],
                ),
                comment['body'],
                created=datetime.strptime(comment['created_at'], _gh_datetime_format),
                ticket=ticket
            )
            komments.append(ticket_comment)
        session.DB.session.add(ticket)
    session.DB.session.commit()
    return tickets, komments


def create_work_repo(project_id, account_id):
    session = make_admin_github_session(account_id)
    config = session.api.oauth.app.config
    from rebase.models import GithubProject
    project = GithubProject.query.get(project_id)
    if not project:
        return 'Unknow project with id: {}'.format(project_id)
    repo_full_path = project.work_repo.full_repo_path
    if call(['ls', repo_full_path]) == 0:
        return 'Repo already exists, skipping.'
    check_call(['git', 'init', repo_full_path])
    oauth_url = project.remote_repo.url.replace('https://api.github.com', 'https://'+session.account.access_token+'@github.com', 1)
    oauth_url = oauth_url.replace('github.com/repos', 'github.com', 1)
    check_call(['git', '-C', repo_full_path, 'pull', oauth_url])


def save_comment(account_id, comment_id):
    session = make_admin_github_session(account_id)
    from rebase.models import Comment
    new_comment = Comment.query.get(comment_id)
    if not new_comment:
        warning('There is no comment with id %d', comment_id)
    else:
        logger.info('Push new comment to Github: %s', new_comment)
        response = session.api.post(
            '{repo_url}/issues/{number}/comments'.format(
                repo_url=new_comment.ticket.project.remote_repo.url,
                number=new_comment.ticket.number
            ),
            data={ 'body': new_comment.content},
            format='json'
        )
        if response.status > 201:
            logger.debug('status: %s', response.status)
            logger.debug('data: %s', response.data)
