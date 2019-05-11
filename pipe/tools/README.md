name
  The name of the tool.

fields
  The fields that will be passed between methods of this tool.

methods
  The order in which methods on the tool will be called.

  module (list) REQUIRED
    If this method must be run and cannot be skipped, and this module is
    not available, error.

  prompt (Boolean)
    If prompt exists and is set to true, it will treat the method as a
    prompt (it will spin off a gui thread, so it needs handlers, etc.)

  provides (list)
    The method will provide these outputs, and if they are already provided,
    the method will be skipped.

  needs (list)
    The method will require these inputs, and fail if they do not exist.

  conditional (list)
    The method will provide these outputs conditionally. They are NOT considered
    when deciding whether or not to run the method.

  optional (list)
    The method can take in these inputs, but does not need them.
