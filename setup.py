from setuptools import setup, find_packages

setup(
    name="music_controller",
    version="0.1.0",
    description="A computer vision-based virtual instrument controller",
    author="Kangyi Zhang",
    author_email="kz2643@nyu.edu",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'opencv-python',
        'mediapipe',
        'pyaudio',
        'pillow',
        'unittest'
        'tk'
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'music-controller=music_controller.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
)