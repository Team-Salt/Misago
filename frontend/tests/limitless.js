import assert from 'assert';
import { LimitLess } from 'limitless/index';

var limitless = null;

describe('LimitLess', function() {
  it("addInitializer registers new initializer", function() {
    limitless = new LimitLess();

    limitless.addInitializer({
      name: 'test',
      initializer: null
    });

    assert.equal(limitless._initializers[0].key, 'test',
      "test initializer was registered");

    assert.equal(limitless._initializers.length, 1,
      "addInitializer() registered single initializer in container");
    assert.equal(limitless._initializers[0].key, 'test',
      "addInitializer() registered test initializer in container");
  });

  it("init() calls test initializer", function() {
    limitless = new LimitLess();

    limitless.addInitializer({
      name: 'test',
      initializer: function(limitless) {
        assert.equal(limitless, limitless, "initializer was called with context");
        assert.equal(limitless._context, 'tru', "context is preserved");
      }
    });

    limitless.init('tru');
  });

  it("init() calls test initializers in order", function() {
    limitless = new LimitLess();

    limitless.addInitializer({
      name: 'carrot',
      initializer: function(limitless) {
        assert.equal(limitless._context.next, 'carrot',
          "first initializer was called in right order");

        limitless._context.next = 'apple';
      },
      before: 'apple'
    });

    limitless.addInitializer({
      name: 'apple',
      initializer: function(limitless) {
        assert.equal(limitless._context.next, 'apple',
          "second initializer was called in right order");

        limitless._context.next = 'orange';
      }
    });

    limitless.addInitializer({
      name: 'orange',
      initializer: function(limitless) {
        assert.equal(limitless._context.next, 'orange',
          "pen-ultimate initializer was called in right order");

        limitless._context.next = 'banana';
      },
      before: '_end'
    });

    limitless.addInitializer({
      name: 'banana',
      initializer: function(limitless) {
        assert.equal(limitless._context.next, 'banana',
          "ultimate initializer was called in right order");
      },
      after: 'orange'
    });

    limitless.init({next: 'carrot'});
  });

  it("has() tests if context has value", function() {
    limitless = new LimitLess();
    limitless.init({valid: 'okay'});

    assert.equal(limitless.has('invalid'), false,
      "has() returned false for nonexisting key");
    assert.equal(limitless.has('valid'), true,
      "has() returned true for existing key");
  });

  it("get() allows access to context values", function() {
    limitless = new LimitLess();
    limitless.init({valid: 'okay'});

    assert.equal(limitless.get('invalid'), undefined,
      "get() returned undefined for nonexisting key");
    assert.equal(limitless.get('invalid', 'fallback'), 'fallback',
      "get() returned fallback value for nonexisting key");
    assert.equal(limitless.get('valid'), 'okay',
      "get() returned value for existing key");
    assert.equal(limitless.get('valid', 'fallback'), 'okay',
      "get() returned value for existing key instead of fallback");
  });

  it("pop() allows single time access to context values", function() {
    limitless = new LimitLess();
    limitless.init({valid: 'okay'});

    assert.equal(limitless.pop('invalid'), undefined,
      "pop() returned undefined for nonexisting key");
    assert.equal(limitless.pop('valid'), 'okay',
      "pop() returned value for existing key");
    assert.equal(limitless.get('valid'), null,
      "get() returned null for popped value");
  });
});
