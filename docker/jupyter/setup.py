from setuptools import setup, find_packages


with open('./docker/jupyter/requirements.txt') as requirements_txt:
    requirements = [ line for line in requirements_txt ]


setup(
    name='rebase-jupyter',
    version='0.1.0',
    description='Jupyter for Rebase',
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
    keywords='rebase jupyter api',
    packages=find_packages(
        exclude=[
            'tests',
            'rebase/views',
        ]
    ),
    install_requires=requirements,
    extras_require=dict(),
    package_data=dict(),
    data_files=[],
    entry_points=dict(),
)


