openapi = {
    "openapi": "3.0.0",
    "info": {
        "title": "unrest.tests.flask.conftest unrest api",
        "version": "1.0"
    },
    "servers": [{
        "url": "http://localhost/api/"
    }],
    "paths": {
        "/fruit": {
            "summary": "A bag of fruit",
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
                                                "$ref":
                                                    "#/components/schemas" +
                                                    "/Fruit"
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
                                                "$ref":
                                                    "#/components/schemas" +
                                                    "/Fruit"
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
                                "$ref": "#/components/schemas/Fruit"
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
                                                "$ref":
                                                    "#/components/schemas" +
                                                    "/Fruit"
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
        "/fruit/{fruit_id}": {
            "summary": "A bag of fruit",
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
                                                "$ref":
                                                    "#/components/schemas" +
                                                    "/Fruit"
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
                    "required": True
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
                                                "$ref":
                                                    "#/components/schemas" +
                                                    "/Fruit"
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
                    "required": True
                }],
                "requestBody": {
                    "description": "The Fruit object to create or replace",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Fruit"
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
                                                "$ref":
                                                    "#/components/schemas" +
                                                    "/Fruit"
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
                    "required": True
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
                                                "$ref":
                                                    "#/components/schemas" +
                                                    "/Fruit"
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
                    "required": True
                }],
                "requestBody": {
                    "description": "The Fruit object patches.",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Fruit"
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
                                                "$ref":
                                                    "#/components/schemas" +
                                                    "/Fruit"
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
                    "required": True
                }]
            }
        },
        "/tree": {
            "summary": "Where money doesn't grow",
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                        "The new Tree objects to replace the current " +
                        "collection with",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "objects": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/Tree"
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                                "$ref": "#/components/schemas/Tree"
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                                            "$ref": "#/components/schemas/Tree"
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
        "/tree/{id}": {
            "summary": "Where money doesn't grow",
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                    "required": True
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                    "required": True
                }],
                "requestBody": {
                    "description": "The Tree object to create or replace",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Tree"
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                    "required": True
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                    "required": True
                }],
                "requestBody": {
                    "description": "The Tree object patches.",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Tree"
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
                                                "$ref":
                                                    "#/components/schemas/Tree"
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
                    "required": True
                }]
            }
        }
    },
    "components": {
        "schemas": {
            "Fruit": {
                "type": "object",
                "properties": {
                    "fruit_id": {
                        "type": "integer",
                        "format": "int64"
                    },
                    "color": {
                        "type": "string",
                        "format": "str"
                    },
                    "age": {
                        "type": "number",
                        "format": "timedelta"
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
            },
            "Tree": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "format": "int64"
                    },
                    "name": {
                        "type": "string",
                        "format": "str"
                    }
                }
            }
        }
    }
}
