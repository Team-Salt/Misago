import assert from 'assert';
import { StoreWrapper } from 'limitless/services/store';
import reducer, { initialState, doTick } from 'limitless/reducers/tick';

let store = null;

describe("Tick", function() {
  beforeEach(function() {
    store = new StoreWrapper();
    store.addReducer('tick', reducer, initialState);
    store.init();
  });

  it("tick action increases ticks count", function() {
    store.dispatch(doTick());
    assert.equal(store.getState().tick.tick, 1, "tick was counted");

    store.dispatch(doTick());
    assert.equal(store.getState().tick.tick, 2, "tick was counted again");
  });
});