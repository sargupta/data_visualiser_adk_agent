from setuptools import setup, find_packages

setup(
    name="visualization-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "adk",
        "pandas",
        "plotly",
        "dash",
        "httpx",
        "certifi",
        "urllib3",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A visualization agent using ADK for data visualization",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/visualization-agent",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
