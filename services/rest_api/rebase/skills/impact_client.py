from logging import getLogger

from .technology_impact_service import TechnologyImpactService

LOGGER = getLogger(__name__)

# crappy hack for now
LANGUAGE_IMPACTS = { 'Python': 8000000, 'JavaScript': 12000000 }

class ImpactClient(object):
    
    def __init__(self):
      self.clients = {
          'Python': TechnologyImpactService('impact_python'),
          'Javascript': TechnologyImpactService('impact_javascript'),
          # 'Java': TechnologyImpactService('impact_java'),
          }

    def score(self, language, context = None, package = None):
        LOGGER.debug('language is {}'.format(language))
        LOGGER.debug('package is {}'.format(package))
        if not package:
            LOGGER.debug('no package!')
            return LANGUAGE_IMPACTS[language] if language in LANGUAGE_IMPACTS else 0
        elif context != '3rd-party':
            LOGGER.debug('not third party!')
            return LANGUAGE_IMPACTS[language] if language in LANGUAGE_IMPACTS else 0        
        else:
            LOGGER.debug('actually doing the work')
            return self.clients[language].get_impact(package) if language in self.clients else 0
    
