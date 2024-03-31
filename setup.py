from setuptools import setup, find_packages

setup(
    name='pyllm',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'llm = llm.main:main'
        ]
    },
    install_requires=[
        'rich',
        'anthropic'
    ],
)