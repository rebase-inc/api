from setuptools import setup, find_packages


with open('./docker/web/requirements.txt') as requirements_txt:
    requirements = [ line for line in requirements_txt ]


setup(
    name='web',
    version='0.1.0',
    description='Web API',
    long_description='',
    url='https://joinrebase.com',
    author='Raphael Goyran',
    author_email='raphael@joinrebase.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Developer Ranking and Remote Work Marketplace',
        'License :: Rebase Terms of Use (TBD!!!)',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='rebase api code2resume',
    packages=find_packages(
        exclude=[
            'tests',
            'rebase/views',
        ]
    ),
    install_requires=requirements,
    entry_points={
        'console_scripts': ['cache=rebase.scripts.cache:main']
    }
)


