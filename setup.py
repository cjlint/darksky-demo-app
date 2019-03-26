from setuptools import setup, find_packages

setup(
    name="cat_mood",
    version="0.1.0",
    packages=find_packages(),
    package_data={"cat_mood": ["static/*"]},
    entry_points={"console_scripts": ["cat-mood-service=cat_mood.main:main"]},
    install_requires=["requests", "flask", "requests-cache"],
)
