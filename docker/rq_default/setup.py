from pprint import pprint
from setuptools import setup, find_packages


with open('./docker/rq_default/requirements.txt') as requirements_txt:
    requirements = [ line for line in requirements_txt ]


packages=find_packages(
    exclude=[
        'parsers',
        'rebase.common.settings.population',
        'rebase.common.settings.web',
        'rebase.git',
        'rebase.home',
        'rebase.resources',
        'rebase.tests',
        'rebase.tests.*',
        'rebase.views',
    ]
)


pprint(packages)


setup(
    name='rq_default',
    version='0.1.0',
    description='default data reducer',
    long_description='',
    url='https://joinrebase.com',
    author='Raphael Goyran',
    author_email='raphael@joinrebase.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Developer Ranking and Remote Work Marketplace',
        'License :: Rebase Terms of Use (TBD!!!)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='rebase api code2resume',
    packages=packages,
    install_requires=requirements,
    extras_require=dict(),
    package_data=dict(),
    data_files=[],
    entry_points={
        'console_scripts': [
            'rq_default=rebase.scripts.rq_default:main',
            'py2_parser=rebase.scripts.parse_python2:main',
        ]
    }
)


