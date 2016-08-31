from builtins import object


class TechnologyScanner(object):

    def extract_library_bindings(self, code, filename):
        raise NotImplemented('Abstract method TechnologyScanner.extract_library_bindings')

    def grammar_use(self, code, date):
        raise NotImplemented('Abstract method TechnologyScanner.grammar_use')

    def libraries_profile(code, library_bindings, date):
        '''
            Return a TechProfile object for libraries from 'code'.
        '''
        profile = TechProfile()
        for module, bindings in iteritems(library_bindings):
            for binding in bindings:
                for line in code.splitlines():
                    if binding in line:
                        profile.add(module, date, 1)
        #pdebug(profile, 'Libraries profile')
        return profile

    def language_profile(new_code, old_code, filename, date):
        new_grammar_use = self.grammar_use(new_code, date)
        if not old_code:
            return new_grammar_use
        old_grammar_use = self.grammar_use(old_code, date)
        abs_diff = TechProfile()
        all_keys = set(new_grammar_use) | set(old_grammar_use)
        for technology in all_keys:
            # not the best option, but until we can diff 2 abstract syntax trees,
            # we can only look at the aggregate change
            use_count = abs(new_grammar_use[technology].total_reps - old_grammar_use[technology].total_reps)
            if use_count > 0:
                abs_diff.add(technology, date, use_count)
        return abs_diff

    def scan_contents(self, filename, code, date):
        '''
            Return a TechProfile object for 'code'
        '''
        raise NotImplemented('Abstract method TechnologyScanner.scan_contents')

    def scan_patch(self, filename, code, previous_code, patch, date):
        '''
            Return a TechProfile object for the modified 'code'
        '''
        # taken the original patch and remove:
        # - context lines
        # - deleted lines
        # - comments
        reduced_patch = []
        for line in patch.splitlines():
            if line.startswith('+'):
                line = line[1:].lstrip()
                if line:
                    if line[0] == '#':
                        continue
                    reduced_patch.append(line)
        library_bindings = self.extract_library_bindings(code, filename)
        complete_profile = libraries_profile('\n'.join(reduced_patch), library_bindings, date)
        complete_profile.merge(language_profile(code, previous_code, filename, date))
        return complete_profile


