from flask import render_template
from flask.ext.login import current_user

from rebase.models.user import User
from rebase.models.skill_set import SkillSet
from rebase.models.contractor import Contractor

def register_home(app):
    @app.route('/')
    def login_root():
        if current_user.is_authenticated():
            user = User.query.filter(User.id==current_user.id).first()
            skill_set = SkillSet.query.join(Contractor).filter(Contractor.user==user).first()
            languages = None
            if skill_set:
                languages = skill_set.skills
            return render_template(
                'main.html',
                first = user.first_name,
                last=user.last_name,
                email=user.email,
                languages=languages
            )
        else:
            return render_template('login.html')
