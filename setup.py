import setuptools


setuptools.setup(
    name="rtl_433_exporter",
    version="0.0.1",
    author="Steven Brudenell",
    author_email="steven.brudenell@gmail.com",
    packages=setuptools.find_packages(),
    install_requires=[
        "prometheus_client>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "rtl_433_exporter = rtl_433_exporter:exporter_main",
        ],
    },
)
