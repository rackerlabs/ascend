import setuptools

setuptools.setup(
    name='ascend',
    version='0.1',
    description=('Utility for automating group, policies, webhooks, and '
                 'launch configuration setup for Rackspace Autoscale'),
    long_description=open('README.rst').read(),
    keywords='rackspace autoscale cloud',
    author='Dave Kludt',
    author_email='david.kludt@rackspace.com',
    url='https://github.com/rackerlabs/ascend',
    license='Apache License, Version 2.0',
    py_modules=['ascend'],
    install_requires=[
        'argparse>=1.2.1',
        'requests>=2.2.1'
    ],
    entry_points={
        'console_scripts': [
            'ascend=ascend:shell'
        ]
    },
    classifiers=[
        'Programming Language :: Python',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Idependent'
    ]
)