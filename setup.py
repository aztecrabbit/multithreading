import setuptools

with open('README.md', 'r') as fh:
	long_description = fh.read()

setuptools.setup(
	name='multithreading',
	version='0.1.7',
	author='aztecrabbit',
	author_email='ars.xda@gmail.com',
	description='MultiThreading: Thread + Queue',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/aztecrabbit/multithreading',
	packages=setuptools.find_packages(),
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	python_requires='>=3.8',
)
