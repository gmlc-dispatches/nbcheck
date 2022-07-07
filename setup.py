from setuptools import setup, find_packages


setup(
    name="dispatches-nbcheck",
    author="Ludovico Bianchi",
    author_email="lbianchi@lbl.gov",
    setup_requires=["setuptools_scm"],
    use_scm_version={
        "version_scheme": "post-release",
    },
    install_requires=[
        "pytest",
        "nbformat",
        "nbval",
    ],
    entry_points={
        "pytest11": [
            "nbcheck = nbcheck.pytest_plugin:plugin"
        ]
    },
    classifiers=[
        "Framework :: Pytest",
    ]
)
