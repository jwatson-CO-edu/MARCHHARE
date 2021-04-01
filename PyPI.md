https://packaging.python.org/tutorials/packaging-projects/
1. The token for the test server is different from the main server.
1. When a new version is ready to test:  
`python3 -m build`
2. Upload to PyPI:  
`python3 -m twine upload --repository pypi dist/*`  
    * Username: `__token__`
    * Password: "Entire contents of the file, including the pypi- prefix"
3. Install:  
`python3 -m pip install marchhare`