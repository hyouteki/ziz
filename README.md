## Objective
Extract all fields from collection of general form/portal website. And present a unified set of fields which are required to autofill all the portals.

## Solves
1. Deprecate manual handling of required fields.
2. Easily employable when any portal updates.
3. Easily scalable.

## ToDo
- [x] Should be able to extract fields from any general form/portal website.
- [ ] Suppose their are fields such as 'fname' and 'firstname'; the script should be able to deduce that both fields essentially means the same thing. *NLP can be employed here.*
- [ ] Should be able to work with multiple-page forms.
- [ ] Remove non-meaningful fields from the extract set of fields. Fields those are essential for the working of form but not needed to be handled by the user should be removed. *NLP can be employed here.*
