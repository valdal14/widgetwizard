import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='widgetwizard',
    version='0.3.0',
    author="Valerio D'Alessio - @valdal14",
    author_email="valerio.dalessio@oracle.com",
    license='MIT',
    description="Widget Wizard is a Python automation module that allows you to create widget and extension code base structures for your Oracle Commerce Cloud projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/valdal14/widgetwizard",
    packages=setuptools.find_packages(),
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
    dependency_links=[
        'https://github.com/psf/requests.git'
    ],
    python_requires='>=3.7.1',
 )


