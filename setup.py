from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name="Flask-Matomo-D",
    version="0.0.3",
    url="https://github.com/firefresh/flask-matomo-d",
    license="",
    author="Demetrio Dowbnac",
    author_email="demetriodowbnac@gmail.com",
    description="Track requests to your Flask website with Matomo ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["flask_matomo"],
    zip_safe=False,
    include_package_data=True,
    install_requires=["Flask"],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
