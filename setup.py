from setuptools import setup, find_packages


setup(
    name="dispatches-nbcheck",
    author="Ludovico Bianchi",
    author_email="lbianchi@lbl.gov",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
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
