from setuptools import setup, find_packages

setup(
    name='rq-population',
    version='0.1.0',
    description='Population data reducer',
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
    install_requires=[
		'aniso8601==1.1.0',
		'blinker==1.4',
		'boto3==1.4.0',
		'botocore==1.4.56',
		'click==6.6',
		'docutils==0.12',
		'Flask==0.11.1',
		'Flask-Cache==0.13.1',
		'Flask-Login==0.3.2',
		'Flask-RESTful==0.3.5',
		'Flask-SQLAlchemy==2.1',
		'future==0.15.2',
		'itsdangerous==0.24',
		'Jinja2==2.8',
		'jmespath==0.9.0',
		'MarkupSafe==0.23',
		'marshmallow==2.6.1',
		'psycopg2==2.6.1',
		'python-dateutil==2.5.2',
		'pytz==2016.4',
		'redis==2.10.5',
		'requests==2.9.1',
		'rq==0.6.0',
		's3transfer==0.1.4',
		'six==1.10.0',
		'Werkzeug==0.11.11',
    ],
    extras_require=dict(),
    package_data=dict(),
    data_files=[],
    entry_points={
        'console_scripts': ['population=rebase.population:main']
    }
)


