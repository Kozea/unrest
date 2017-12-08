0.6.8
=====

* Return a 404 with json on GET for an unknown id.

0.6.7
=====

* Add schema for parameter in openapi apparently required according to last swagger commit.

0.6.6
=====

* Add openapi.json file generation
* Rewrite OPTIONS generation

0.6.5
=====

* Fix deferrable columns crash.
* Add missing default float serializer/deserializer.

0.6.4
=====

* Don't flush before validating item creation (POST)

0.6.3
=====

* Add previous and next item in Validatable to allow cross field validation.
* Allow field validator lists in validators.
* Disable autoflush while validating to prevent sql errors.

0.6.2
=====

* Run test before releasing (...) fix validation bug introduced in 0.6.1

0.6.1
=====

* Add a primary_keys argument to rest endpoints.
* Fix bug when putting a element that didn't exist.

0.6.0
=====

* Fix a design flaw in route naming being the same with diferent unrest path.


0.5.1
=====

* Add ValidationError on Validatable to avoid the need of having a unrest instance.

0.5.0
=====

* Add validators argument to Rest to provide a mapping of field validators for incoming data.


0.4.1
=====

* Add the possibility of returning a response wrapper in auth decorators.

0.4.0
=====

* Handle pagination by returning correct number of total occurences without any limit/offset. Returns limit and offset if any.


0.3.1
=====

* Handle prioritarly Model.query queries if exist.

0.3.0
=====

* Add PATCH method


0.2.4
=====

* Add primary_keys in json response

0.2.3
=====

* Add extra data on errors

0.2.2
=====

* Add default coercer for large binary type to base64

0.2.0
=====

* Handle correctly columns with a different name in mapping
