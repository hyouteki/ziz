## Objective
Extract all fields from collection of general form/portal website. And present a unified set of fields which are required to autofill all the portals.

## Solves
1. Deprecate manual handling of required fields.
2. Easily employable when any portal updates.
3. Easily scalable.

## Todo
- [x] Should be able to extract fields from any general form/portal website.
- [ ] Handle cases where field properties differ from standard conventions (e.g., 'ng-reflect-name' instead of 'name' as used in https://rpachallenge.com).
- [x] Suppose their are fields such as 'fname' and 'firstname'; the script should be able to deduce that both fields essentially means the same thing. *NLP can be employed here.*
- [ ] Should be able to work with multiple-page forms.
- [x] Remove non-meaningful fields from the extract set of fields. Fields those are essential for the working of form but not needed to be handled by the user should be removed. *NLP can be employed here.*
- [x] Sample Test environment.

## Getting Started
Setup a python virtual environment and activate it, follow [this](https://docs.python.org/3/library/venv.html) if you don't know how to.
```bash
pip install .
```
Start test server
```bash
cd tests
node server.js
cd ..
```
Test the tool
```bash
python ziz.py
```
