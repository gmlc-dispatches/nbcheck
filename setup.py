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
        "pytest >= 7",
        "nbformat",
        # we use a relatively tight pinning for nbval
        # since we rely on several non-CLI APIs directly
        "nbval ~= 0.10",
        "ipykernel",  # ipykernel.kernelspec
    ],
    packages=find_packages(),
    entry_points={
        "pytest11": [
            "nbcheck = nbcheck.plugin",
        ],
        "nbcheck": [
            "execution = nbcheck.execution",
            "headers = nbcheck.headers",
            "cell_order = nbcheck.cell_order",
        ],
    },
    classifiers=[
        "Framework :: Pytest",
    ]
)
