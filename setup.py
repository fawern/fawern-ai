from setuptools import setup, find_packages

setup(
    name="fawern", 
    version="0.2.5",
    author="Enes Ekinci",  
    author_email="ekincimuhammedenes13@gmai.com",  
    description="Fawern AI, A Python Developer AI Assistant", 
    long_description=open('README.md').read(),  
    long_description_content_type="text/markdown",
    url="https://github.com/fawern/fawern_ai",
    packages=find_packages(),
    install_requires=[
        'groq==0.9.0',
        'openai>=1.0.0',
        'python-dotenv==1.0.1',
        'setuptools==69.0.3',
        'PyYAML==6.0.1',
    ],
    license="MIT",
    classifiers=[  
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6', 
)
