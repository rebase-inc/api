from .technology_impact_service import TechnologyImpactService

# crappy hack for now
LANGUAGE_IMPACTS = { 'Python': 800000 }

class ImpactClient(object):
    
    def __init__(self):
      self.clients = {
          'Python': TechnologyImpactService('impact_python'),
          # 'JavaScript': TechnologyImpactService('impact_javascript'),
          # 'Java': TechnologyImpactService('impact_java'),
          }

    def score(self, language, context = None, package = None):
        if not package:
            return LANGUAGE_IMPACTS[language] if language in LANGUAGE_IMPACTS else 0
        elif context != '3rd-party':
            return LANGUAGE_IMPACTS[language] if language in LANGUAGE_IMPACTS else 0        
        else:
            return self.clients[language].get_impact(package) if language in self.clients else 0
    
