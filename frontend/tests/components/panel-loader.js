import assert from 'assert';
import React from 'react'; // jshint ignore:line
import PanelLoader from 'limitless/components/panel-loader'; // jshint ignore:line
import * as testUtils from 'limitless/utils/test-utils';

describe("Panel Loader", function() {
  afterEach(function() {
    testUtils.unmountComponents();
  });

  it("renders", function() {
    /* jshint ignore:start */
    testUtils.render(<PanelLoader />);
    /* jshint ignore:end */

    assert.ok($('#test-mount .panel-body-loading .loader').length,
      "component renders");
  });
});
