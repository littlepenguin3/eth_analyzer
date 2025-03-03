from setuptools import setup, find_packages

setup(
    name="eth_analyzer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "clickhouse-driver>=0.2.5",
        "pandas>=1.3.0",
        "PyYAML>=6.0",
        "numpy>=1.21.0",
        "python-dateutil>=2.8.2",
        "pytz>=2021.1",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "jupyter>=1.0.0",
        "ipython>=7.31.0"
    ],
    python_requires=">=3.8",
    author="ETH Analyzer Team",
    description="以太坊区块链数据分析工具",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
) 