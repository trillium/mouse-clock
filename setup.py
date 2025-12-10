from setuptools import setup, find_packages

setup(
    name='mouse-clock',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A Python tool for repositioning the mouse using voice commands mapped to a clock representation.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'talon',  # Assuming Talon is a dependency
        'some-voice-recognition-library',  # Replace with actual library if needed
        'some-gui-library'  # Replace with actual library if needed
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)