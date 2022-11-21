from setuptools import setup, find_packages

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='indent',
    version='1.0.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    description='Context manager for indenting text',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/myarcana/indent.py/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3 :: Only'
    ],
    python_requires='>=3.7, <4',
    project_urls={
        'Bug Reports': 'https://github.com/myarcana/indent.py/issues',
        'Source': 'https://github.com/myarcana/indent.py/'
    }
)
