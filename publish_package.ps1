& venv/Scripts/Activate.ps1
Remove-Item -Recurse -Force dist
Remove-Item -Recurse -Force build
& python setup.py sdist
& python setup.py bdist_wheel
& python -m twine upload dist/*
pause