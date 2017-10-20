openapi = {
    "openapi": "3.0.0",
    "info": {
        "title":
            "unrest.tests.flask.conftest unrest api",
        "version":
            "1.0",
        "description":
            "# Unrest demo\nThis is the demo of unrest api.\n" +
            "This api expose the `Tree` and `Fruit` entity Rest methods.\n",
        "contact": {
            "name": "Florian Mounier",
            "url": "https://github.com/Kozea/unrest",
            "email": "florian.mounier@kozea.fr"
        },
        "license": {
            "name": "GNU LGPL v3+"
        }
    },
    "servers": [{
        "url": "http://localhost/api/"
    }],
    "paths": {
        "/fruit": {
            "get": {
                "tags": ["Fruit"],
                "summary": "Retrieve all Fruit objects",
                "responses": {
                    "200": {
                        "description": "All Fruit objects",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "fruit_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "color": {
                                                        "type": "string"
                                                    },
                                                    "age": {
                                                        "type": "number"
                                                    },
                                                    "size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    },
                                                    "tree_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "square_size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Fruit"],
                "summary": "Add a new Fruit object",
                "responses": {
                    "200": {
                        "description": "The new Fruit object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "fruit_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "color": {
                                                        "type": "string"
                                                    },
                                                    "age": {
                                                        "type": "number"
                                                    },
                                                    "size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    },
                                                    "tree_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "square_size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "requestBody": {
                    "description": "The new Fruit object to create",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "fruit_id": {
                                        "type": "integer",
                                        "format": "int64"
                                    },
                                    "color": {
                                        "type": "string"
                                    },
                                    "age": {
                                        "type": "number"
                                    },
                                    "size": {
                                        "type": "number",
                                        "format": "double"
                                    },
                                    "tree_id": {
                                        "type": "integer",
                                        "format": "int64"
                                    }
                                }
                            }
                        }
                    },
                    "required": True
                }
            },
            "options": {
                "tags": ["Fruit"],
                "summary": "Get info about the Fruit collection",
                "responses": {
                    "200": {
                        "description": "Info about the Fruit collection",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "fruit_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "color": {
                                                        "type": "string"
                                                    },
                                                    "age": {
                                                        "type": "number"
                                                    },
                                                    "size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    },
                                                    "tree_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "square_size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "summary": "A bag of fruit"
        },
        "/fruit/{fruit_id}": {
            "get": {
                "tags": ["Fruit"],
                "summary":
                    "Retrieve the corresponding Fruit object",
                "responses": {
                    "200": {
                        "description": "The corresponding Fruit object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "fruit_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "color": {
                                                        "type": "string"
                                                    },
                                                    "age": {
                                                        "type": "number"
                                                    },
                                                    "size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    },
                                                    "tree_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "square_size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "fruit_id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }]
            },
            "put": {
                "tags": ["Fruit"],
                "summary":
                    "Replace the corresponding Fruit object or create it",
                "responses": {
                    "200": {
                        "description": "The added Fruit object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "fruit_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "color": {
                                                        "type": "string"
                                                    },
                                                    "age": {
                                                        "type": "number"
                                                    },
                                                    "size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    },
                                                    "tree_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "square_size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "fruit_id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }],
                "requestBody": {
                    "description": "The Fruit object to create or replace",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "fruit_id": {
                                        "type": "integer",
                                        "format": "int64"
                                    },
                                    "color": {
                                        "type": "string"
                                    },
                                    "age": {
                                        "type": "number"
                                    },
                                    "size": {
                                        "type": "number",
                                        "format": "double"
                                    },
                                    "tree_id": {
                                        "type": "integer",
                                        "format": "int64"
                                    }
                                }
                            }
                        }
                    },
                    "required": True
                }
            },
            "delete": {
                "tags": ["Fruit"],
                "summary":
                    "Delete the corresponding Fruit object",
                "responses": {
                    "200": {
                        "description": "The deleted Fruit object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "fruit_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "color": {
                                                        "type": "string"
                                                    },
                                                    "age": {
                                                        "type": "number"
                                                    },
                                                    "size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    },
                                                    "tree_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "square_size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "fruit_id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }]
            },
            "patch": {
                "tags": ["Fruit"],
                "summary":
                    "Patch the corresponding Fruit object",
                "responses": {
                    "200": {
                        "description": "The patched Fruit object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "fruit_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "color": {
                                                        "type": "string"
                                                    },
                                                    "age": {
                                                        "type": "number"
                                                    },
                                                    "size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    },
                                                    "tree_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "square_size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "fruit_id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }],
                "requestBody": {
                    "description": "The Fruit object patches.",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "fruit_id": {
                                        "type": "integer",
                                        "format": "int64"
                                    },
                                    "color": {
                                        "type": "string"
                                    },
                                    "age": {
                                        "type": "number"
                                    },
                                    "size": {
                                        "type": "number",
                                        "format": "double"
                                    },
                                    "tree_id": {
                                        "type": "integer",
                                        "format": "int64"
                                    }
                                }
                            }
                        }
                    },
                    "required": True
                }
            },
            "options": {
                "tags": ["Fruit"],
                "summary":
                    "Get info about the Fruit collection",
                "responses": {
                    "200": {
                        "description": "Info about the Fruit collection",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "fruit_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "color": {
                                                        "type": "string"
                                                    },
                                                    "age": {
                                                        "type": "number"
                                                    },
                                                    "size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    },
                                                    "tree_id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "square_size": {
                                                        "type": "number",
                                                        "format": "double"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "fruit_id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }]
            },
            "summary": "A bag of fruit"
        },
        "/tree": {
            "get": {
                "tags": ["Tree"],
                "summary": "Retrieve all Tree objects",
                "responses": {
                    "200": {
                        "description": "All Tree objects",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "put": {
                "tags": ["Tree"],
                "summary": "Replace all Tree objects",
                "responses": {
                    "200": {
                        "description": "The new Tree objects",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "requestBody": {
                    "description":
                        "The new Tree objects to replace the current collection with",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "objects": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "format": "int64"
                                                },
                                                "name": {
                                                    "type": "string"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "required":
                        True
                }
            },
            "post": {
                "tags": ["Tree"],
                "summary": "Add a new Tree object",
                "responses": {
                    "200": {
                        "description": "The new Tree object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "requestBody": {
                    "description": "The new Tree object to create",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "integer",
                                        "format": "int64"
                                    },
                                    "name": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    },
                    "required": True
                }
            },
            "delete": {
                "tags": ["Tree"],
                "summary": "Delete all Tree objects",
                "responses": {
                    "200": {
                        "description": "All deleted Tree objects",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "patch": {
                "tags": ["Tree"],
                "summary": "Patch all Tree objects",
                "responses": {
                    "200": {
                        "description": "The patched Tree objects",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "requestBody": {
                    "description": "The Tree objects patches",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "objects": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "integer",
                                                    "format": "int64"
                                                },
                                                "name": {
                                                    "type": "string"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "required": True
                }
            },
            "options": {
                "tags": ["Tree"],
                "summary": "Get info about the Tree collection",
                "responses": {
                    "200": {
                        "description": "Info about the Tree collection",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "summary": "Where money doesn't grow"
        },
        "/tree/{id}": {
            "get": {
                "tags": ["Tree"],
                "summary": "Retrieve the corresponding Tree object",
                "responses": {
                    "200": {
                        "description": "The corresponding Tree object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }]
            },
            "put": {
                "tags": ["Tree"],
                "summary":
                    "Replace the corresponding Tree object or create it",
                "responses": {
                    "200": {
                        "description": "The added Tree object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }],
                "requestBody": {
                    "description": "The Tree object to create or replace",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "integer",
                                        "format": "int64"
                                    },
                                    "name": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    },
                    "required": True
                }
            },
            "delete": {
                "tags": ["Tree"],
                "summary": "Delete the corresponding Tree object",
                "responses": {
                    "200": {
                        "description": "The deleted Tree object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }]
            },
            "patch": {
                "tags": ["Tree"],
                "summary":
                    "Patch the corresponding Tree object",
                "responses": {
                    "200": {
                        "description": "The patched Tree object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }],
                "requestBody": {
                    "description": "The Tree object patches.",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "integer",
                                        "format": "int64"
                                    },
                                    "name": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    },
                    "required": True
                }
            },
            "options": {
                "tags": ["Tree"],
                "summary": "Get info about the Tree collection",
                "responses": {
                    "200": {
                        "description": "Info about the Tree collection",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "primary_keys": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "occurences": {
                                            "type": "integer"
                                        },
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer",
                                                        "format": "int64"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "fruit_colors": {
                                                        "type": "string"
                                                    },
                                                    "fruits": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "fruit_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "color": {
                                                                    "type":
                                                                        "string"
                                                                },
                                                                "age": {
                                                                    "type":
                                                                        "number"
                                                                },
                                                                "size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                },
                                                                "tree_id": {
                                                                    "type":
                                                                        "integer",
                                                                    "format":
                                                                        "int64"
                                                                },
                                                                "square_size": {
                                                                    "type":
                                                                        "number",
                                                                    "format":
                                                                        "double"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "parameters": [{
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }]
            },
            "summary": "Where money doesn't grow"
        }
    }
}
