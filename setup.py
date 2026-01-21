"""
Setup script for Server Carbon Calculator
"""

from setuptools import setup, find_packages
import os

# Read the README file
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_path, 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='server-carbon-calculator',
    version='1.0.0',
    description='Calculate carbon footprint of GPU and CPU server components',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/server-carbon-calculator',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.7',
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
        ],
    },
    include_package_data=True,
    package_data={
        'server_carbon': [],
    },
    data_files=[
        ('config', ['config/gpuconfigs.json']),
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='carbon footprint, sustainability, GPU, CPU, server, LCA',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/server-carbon-calculator/issues',
        'Source': 'https://github.com/yourusername/server-carbon-calculator',
    },
)





