from rebase.common.mock import create_one_user

class UseCase(object):

    def base_scenario(self, db):
        '''
        This is where you build your use case.
        The return signature of this method is:
                return user_1, user_2, instance_1, instance_2

        Where user_1 and user_2 have both manager and contractor roles.
        '''
        error_msg = '{} does not have an implementation for UseCase.base_scenario'
        raise NotImplemented(error_msg.format(self.__class__.__name__))

    def user_2_as_contractor(self, db):
        _, user_2, instance_1, _ = self.base_scenario(db)
        return user_2, instance_1

    def user_2_as_mgr(self, db):
        _, user_2, _, instance_2 = self.base_scenario(db)
        return user_2, instance_2

    def user_1_as_mgr(self, db):
        user_1, _, instance_1, _ = self.base_scenario(db)
        return user_1, instance_1

    def user_1_as_contractor(self, db):
        user_1, _, _, instance_2 = self.base_scenario(db)
        return user_1, instance_2

    def admin_base(self, db):
        _, _, instance_1, instance_2 = self.base_scenario(db)
        admin_user = create_one_user(db)
        admin_user.admin = True
        db.session.commit()
        return admin_user, instance_1, instance_2

    def admin(self, db):
        admin_user, instance_1, _ = self.admin_base(db)
        return admin_user, instance_1

    def admin_collection(self, db):
        admin_user, instance_1, instance_2 = self.admin_base(db)
        return admin_user, [instance_1, instance_2]
