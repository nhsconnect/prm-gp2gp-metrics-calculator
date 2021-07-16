from setuptools import find_packages, setup

setup(
    name="gp2gp-metrics-calculator",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["python-dateutil>=2.8", "boto3>=1.17.42", "PyArrow>=4.0"],
    entry_points={
        "console_scripts": [
            "metrics-calculator-pipeline=prmcalculator.pipeline.main:main",
        ]
    },
)
