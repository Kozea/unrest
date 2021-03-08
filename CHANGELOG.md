# [1.0.0](https://github.com/Kozea/unrest/compare/0.7.8...1.0.0)

### Breaking Changes
* **Framework API now requires only a register route but the rest function now takes a `Request` and must return a `Response`.**
* **`Property` property `sqlalchemy_type` has been renamed to `type` for compat with columns.**
* **`column_property` are now considered as normal columns.**
* **Overriding existing routes no longer works. (except when using @declare)**
* Auth wrappers now take the request, the payload, and the primary keys as arguments and return the response (so you can alter the response headers).

<hr />

* Add `Request`/`Response` util classes.
* Add an `Idiom` abstraction with converts request to data and data to response.
* Add a `yaml` idiom (`YamlIdiom`).
* Add a `json_server` idiom (`JsonServerIdiom`).
* Add a native python framework implementation (`HTTPServerFramework`).
* Add a tornado framework implementation (`TornadoFramework`).
* Add a sanic implementation (`SanicFramework`).
* Add cleaner examples.
* Expire items after add/edit to refresh `column_property` and externally dependent columns (i.e. FDW).
* Properties can now be used in `primary_keys`.
* Routes are not registered directly anymore which allows late route overriding
  with declare without having the framework to handle route override (most forbid that)
* Add a rest.virtual() method that behaves like rest() but force no HTTP method registration. Useful for relationships.

## [0.7.8](https://github.com/Kozea/unrest/compare/0.7.7...0.7.8)

* Add a `RestClass` option to `UnRest` to allow `Rest` overload

## [0.7.7](https://github.com/Kozea/unrest/compare/0.7.6...0.7.7)

* Add 'fixed' and 'defaults' props in sub rest's route (thanks @Le-Stagiaire, NB: Next time make a PR)

## [0.7.6](https://github.com/Kozea/unrest/compare/0.7.5...0.7.6)

* Fix dateutil import.

## [0.7.5](https://github.com/Kozea/unrest/compare/0.7.4...0.7.5)

* Fix `declare` decorator not returning function.

## [0.7.4](https://github.com/Kozea/unrest/compare/0.7.3...0.7.4)

* Add a `validation_error_code` to change the validation error http status.

## [0.7.3](https://github.com/Kozea/unrest/compare/0.7.2...0.7.3)

* `defaults` and `fixed` attributes can now be callable.

## [0.7.2](https://github.com/Kozea/unrest/compare/0.7.1...0.7.2)

* Add a `defaults` attribute to set column defaults.
* Add a `fixed` attribute to force columns values.

## [0.7.1](https://github.com/Kozea/unrest/compare/0.7.0...0.7.1)

* Add a manual commit flag to `@declare` to prevent auto commit.
* Add log info in unrest.rest.

# [0.7.0](https://github.com/Kozea/unrest/compare/0.6.8...0.7.0)

* Add a `rest.sub` method to generate sub collections endpoint.
* Db session commit is now done in the method wrapper instead of the rest methods. This prevents multi commits when calling multiple rest methods inside a `@declare` for instance. No commit is done on GET methods! -Don't alter db on GETs.-

## [0.6.8](https://github.com/Kozea/unrest/compare/0.6.7...0.6.8)

* Return a 404 with json on GET for an unknown id.

## [0.6.7](https://github.com/Kozea/unrest/compare/0.6.6...0.6.7)

* Add schema for parameter in openapi apparently required according to last swagger commit.

## [0.6.6](https://github.com/Kozea/unrest/compare/0.6.5...0.6.6)

* Add openapi.json file generation
* Rewrite OPTIONS generation

## [0.6.5](https://github.com/Kozea/unrest/compare/0.6.4...0.6.5)

* Fix deferrable columns crash.
* Add missing default float serializer/deserializer.

## [0.6.4](https://github.com/Kozea/unrest/compare/0.6.3...0.6.4)

* Don't flush before validating item creation (POST)

## [0.6.3](https://github.com/Kozea/unrest/compare/0.6.2...0.6.3)

* Add previous and next item in Validatable to allow cross field validation.
* Allow field validator lists in validators.
* Disable autoflush while validating to prevent sql errors.

## [0.6.2](https://github.com/Kozea/unrest/compare/0.6.1...0.6.2)

* Run test before releasing (...) fix validation bug introduced in 0.6.1

## [0.6.1](https://github.com/Kozea/unrest/compare/0.6.0...0.6.1)

* Add a primary_keys argument to rest endpoints.
* Fix bug when putting a element that didn't exist.

# [0.6.0](https://github.com/Kozea/unrest/compare/0.5.1...0.6.0)

* Fix a design flaw in route naming being the same with diferent unrest path.

## [0.5.1](https://github.com/Kozea/unrest/compare/0.5.0...0.5.1)

* Add ValidationError on Validatable to avoid the need of having a unrest instance.

# [0.5.0](https://github.com/Kozea/unrest/compare/0.4.1...0.5.0)

* Add validators argument to Rest to provide a mapping of field validators for incoming data.

## [0.4.1](https://github.com/Kozea/unrest/compare/0.4.0...0.4.1)

* Add the possibility of returning a response wrapper in auth decorators.

# [0.4.0](https://github.com/Kozea/unrest/compare/0.3.1...0.4.0)

* Handle pagination by returning correct number of total occurences without any limit/offset. Returns limit and offset if any.

## [0.3.1](https://github.com/Kozea/unrest/compare/0.3.0...0.3.1)

* Handle prioritarly Model.query queries if exist.

# [0.3.0](https://github.com/Kozea/unrest/compare/0.2.4...0.3.0)

* Add PATCH method

## [0.2.4](https://github.com/Kozea/unrest/compare/0.2.3...0.2.4)

* Add primary_keys in json response

## [0.2.3](https://github.com/Kozea/unrest/compare/0.2.2...0.2.3)

* Add extra data on errors

## [0.2.2](https://github.com/Kozea/unrest/compare/0.2.0...0.2.2)

* Add default coercer for large binary type to base64

# [0.2.0](https://github.com/Kozea/unrest/compare/0.1.9...0.2.0)

* Handle correctly columns with a different name in mapping
