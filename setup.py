from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitcli-automation",
    version="0.1.0",
    author="Adelodunpeter",
    author_email="adelodunpeter24@gmail.com",
    description="User-friendly Git CLI automation tool with interactive menus and visual feedback",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Adelodunpeter25/GitCLI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=[
        "colorama>=0.4.6",
        "yaspin>=2.3.0",
    ],
    extras_require={
        "windows": ["win10toast>=0.9"],
    },
    entry_points={
        "console_scripts": [
            "gitcli=gitcli.cli:main",
        ],
    },
    keywords="git cli automation tool interactive version-control",
    project_urls={
        "Bug Reports": "https://github.com/Adelodunpeter25/GitCLI/issues",
        "Source": "https://github.com/Adelodunpeter25/GitCLI",
    },
)
